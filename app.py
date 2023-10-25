import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from pytube import YouTube
import tempfile
import openai

# Set the OpenAI API key
openai.api_key = "[INSERT YOUR OPENAI API KEY HERE]"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    video_url = request.form.get("video_url")
    openai_key = request.form.get("openai_key")

    if not openai_key:
        return jsonify({"error": "OpenAI API key is required."}), 400
    else:
        openai.api_key = openai_key

    if not video_url:
        return jsonify({"error": "Video URL is required."}), 400

    try:
        # Download YouTube video
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()

        # Save the video in a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file_name = temp_file.name

        stream.download(output_path=os.path.dirname(temp_file_name), filename=os.path.basename(temp_file_name))

        # Transcribe the video using OpenAI's Whisper API
        with open(temp_file_name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        youtube_blog_content = summarize_youtube_video(transcript)
        # Remove the temporary file after transcription
        os.remove(temp_file_name)

        return render_template("index.html", transcription=youtube_blog_content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def summarize_youtube_video(transcript):
  """Generates a summary of a YouTube video using OpenAI GPT-3 and displays a progress bar.

  Args:
    video_link: The URL of the YouTube video to summarize.

  Returns:
    A string containing the summary of the video.
  """

  # Create a directory to store the transcripts
  #if not os.path.exists("transcripts"):
  #  os.mkdir("transcripts")

  # Split the video link to get the video ID
  #video_id = video_link.split("=")[1]

  # Download the transcript of the video
  #transcript = YouTubeTranscriptApi.get_transcript(video_id)

  # Save the transcript to a file
  #with open(os.path.join("transcripts", f"{video_id}.txt"), "w") as f:
  #  for line in transcript:
  #    f.write(f"{line['text']}\n")

  # Read the transcript from the file
  #with open(os.path.join("transcripts", f"{video_id}.txt"), "r") as f:
  #  transcript = f.read()

  # Generate a summary of the transcript
  summarized_text = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system",
            "content": """Act as an expert copywriter specializing in content optimization for SEO. Your task is to take a given YouTube    transcript and transform it into a well-structured and engaging article. Your objectives are as follows:

    Content Transformation: Begin by thoroughly reading the provided YouTube transcript. Understand the main ideas, key points, and the overall message conveyed.

    Sentence Structure: While rephrasing the content, pay careful attention to sentence structure. Ensure that the article flows logically and coherently.

    Keyword Identification: Identify the main keyword or phrase from the transcript. Its crucial to determine the primary topic that the YouTube video discusses.

    Keyword Integration: Incorporate the identified keyword naturally throughout the article. Use it in headings, subheadings, and within the body text. However, avoid overuse or keyword stuffing, as this can negatively affect SEO.

    Unique Content: Your goal is to make the article 100% unique. Avoid copying sentences directly from the transcript. Rewrite the content in your own words while retaining the original message and meaning.

    SEO Friendliness: Craft the article with SEO best practices in mind. This includes optimizing meta tags (title and meta description), using header tags appropriately, and maintaining an appropriate keyword density.

    Engaging and Informative: Ensure that the article is engaging and informative for the reader. It should provide value and insight on the topic discussed in the YouTube video.
        Proofreading: Proofread the article for grammar, spelling, and punctuation errors. Ensure it is free of any mistakes that could detract from its quality.

    By following these guidelines, create a well-optimized, unique, and informative article that would rank well in search engine results and engage readers effectively."""
            },
            {
                "role": "user",
                "content": f"""Craft blog content for the text given below.
                Text: {transcript}

                Add a title, make sure your content has useful and true information about the main points of the topic.
                Begin with a introduction explaining the topic. If you can, use bullet points to list important details,
                and finish your content with a summary.""",
            },
        ],
        max_tokens=4096,
        temperature=1,
    )

  if "choices" in summarized_text and len(summarized_text["choices"]) > 0:
    return summarized_text["choices"][0]["message"]["content"]
  else:
    return None


if __name__ == "__main__":
    app.run(debug=True)
