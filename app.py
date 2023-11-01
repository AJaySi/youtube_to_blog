import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from pytube import YouTube
import tempfile
import openai
from html2image import Html2Image

# Set the OpenAI API key
openai.api_key = "[INSERT YOUR OPENAI API KEY HERE]"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["GET", "POST"])
def transcribe():
    app.logger.info("Starting ")
    video_url = request.form.get("video_url")
    openai_key = request.form.get("openai_key")
    # Split the video link to get the video ID
    vid_id = video_url.split("=")[1]
    hti = Html2Image(output_path="static/css/images")
    hti.screenshot(url=video_url, save_as=f"yt-img-{vid_id}.png")
    app.logger.info(f"Saved the YT screenshot:{vid_id}")
    if not openai_key:
        return jsonify({"error": "OpenAI API key is required."}), 400
    else:
        openai.api_key = openai_key

    if not video_url:
        return jsonify({"error": "Video URL is required."}), 400

    try:
        # Download YouTube video
        app.logger.info("Download the YT video.")
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()

        # Save the video in a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file_name = temp_file.name

        stream.download(output_path=os.path.dirname(temp_file_name), filename=os.path.basename(temp_file_name))

        # Transcribe the video using OpenAI's Whisper API
        app.logger.info(f"Saved the YT video: {temp_file_name}, transcribing..")
        with open(temp_file_name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        youtube_blog_content = summarize_youtube_video(transcript)
        # Convert the output to HTML format.
        app.logger.info(f"Convert the markdown blog into HTML.")
        blog_html = convert_markdown_to_html(youtube_blog_content)
        # Remove the temporary file after transcription
        os.remove(temp_file_name)

        return render_template("index.html", img_src=f"static/css/images/yt-img-{vid_id}.png", transcription=blog_html)

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
            model = "gpt-3.5-turbo-16k",
            messages = [
                {
        "role": "system",
        "content": """
        You are an expert copywriter specializing in content optimization for SEO. Your task is to transform a given YouTube transcript into a well-structured and engaging article. Your objectives include:

        1. Master the Transcript: Understand main ideas, key points, and the core message.
        2. Sentence Structure: Rephrase while preserving logical flow and coherence.
        3. Identify Main Keyword: Determine the primary video topic.
        4. Keyword Integration: Naturally integrate keywords in headings, subheadings, and body text, avoiding overuse.
        5. Write Unique Content: Avoid direct copying; rewrite in your own words.
        6. Optimize for SEO: Implement meta tags, header tags, and appropriate keyword density.
        7. Craft Engaging and Informative Article: Provide value and insight to readers.
        8. Proofread: Check for grammar, spelling, and punctuation errors.
        9. Use Creative and Human-like Style: Incorporate contractions, idioms, transitional phrases, interjections, and colloquialisms. Avoid repetitive phrases and unnatural sentence structures.
        10. Structuring: Include a Creative Title, SEO Meta-description, ## Introduction ##, bullet points or numbered lists if appropriate, FAQs, and Conclusion.
        11. Ensure Uniqueness: Guarantee the article is plagiarism-free.
        12. Punctuation: Use appropriate question marks at the end of questions.
        13. Pass AI Detection Tools: Create content that easily passes AI plagiarism detection tools.

        Follow these guidelines to create a well-optimized, unique, and informative article that will rank well in search engine results and engage readers effectively.
        """
    },  
          {
                "role": "user",
                "content": f"""Craft blog content for the given Text.
                Text: {transcript}""",
            },
        ],
        max_tokens=4096,
        temperature=1,
    )

  if "choices" in summarized_text and len(summarized_text["choices"]) > 0:
    return summarized_text["choices"][0]["message"]["content"]
  else:
    return None


def convert_markdown_to_html(md_content):
    """ Helper function to convert given text to HTML 
    """
    html_response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo-16k",
          messages=[ 
            {"role": "system", "content": """
Convert Markdown to HTML:
You are a skilled developer tasked with converting a Markdown-formatted text to HTML. You will be given text in markdown format. Follow these steps to perform the conversion:

1. Parse User's Markdown Input: You will receive a Markdown-formatted text as input from the user. Carefully analyze the provided Markdown text, paying attention to different elements such as headings (#), lists (unordered and ordered), bold and italic text, links, images, and code blocks.
2. Generate and Validate HTML: Generate corresponding HTML code for each Markdown element following the conversion guidelines below. Ensure the generated HTML is well-structured and syntactically correct.
3. Preserve Line Breaks: Markdown line breaks (soft breaks) represented by two spaces at the end of a line should be converted to <br> tags in HTML to preserve the line breaks.
4. REMEMBER to generate complete, valid HTML response only.

Follow below Conversion Guidelines:
- Headers: Convert Markdown headers (#, ##, ###, etc.) to corresponding HTML header tags (<h1>, <h2>, <h3>, etc.).
- Lists: Convert unordered lists (*) and ordered lists (1., 2., 3., etc.) to <ul> and <ol> HTML tags, respectively. List items should be enclosed in <li> tags.
- Emphasis: Convert bold (**) and italic (*) text to <strong> and <em> HTML tags, respectively.
- Links: Convert Markdown links ([text](url)) to HTML anchor (<a>) tags. Ensure the href attribute contains the correct URL.
- Images: Convert Markdown image tags (![alt text](image_url)) to HTML image (<img>) tags. Include the alt attribute for accessibility.
- Code: Convert inline code (`code`) to <code> HTML tags. Convert code blocks (```) to <pre> HTML tags for preserving formatting.
- Blockquotes: Convert blockquotes (>) to <blockquote> HTML tags.
"""
},
            {"role": "user", "content": f"Convert the following Markdown text to HTML:\n\n{md_content}"}
        ],
          max_tokens=8192,
          temperature=1,
          n=1,
    )
    logger.info("Finished converting markdown to html.")
    if "choices" in html_response and len(html_response["choices"]) > 0:
      return html_response["choices"][0]["message"]["content"]
    else:
      return None


if __name__ == "__main__":
    app.run(debug=True)
