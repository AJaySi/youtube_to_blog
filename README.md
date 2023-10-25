## Overview

This Flask application provides a simple way to transcribe YouTube videos and generate blog content using OpenAI's Whisper and GPT-3 APIs.

## Usage

To use the application, simply visit the homepage and enter the URL of the YouTube video you want to transcribe and summarize. You will also need to enter your OpenAI API key. Once you have entered the required information, click the "Transcribe" button.

The application will then download the YouTube video, transcribe it using OpenAI's Whisper API, and generate a summary of the video using OpenAI's GPT-3 API. The summary will be displayed on the homepage.

## Example

To transcribe and summarize the YouTube video with the URL https://www.youtube.com/watch?v=dQw4w9WgXcQ, you would enter the following information into the form on the homepage:

Video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
OpenAI API key: [YOUR_OPENAI_API_KEY]

Once you have entered this information, click the "Transcribe" button.

The application will then download the YouTube video, transcribe it using OpenAI's Whisper API, and generate a summary of the video using OpenAI's GPT-3 API. The summary will be displayed on the homepage.
Requirements

    Python 3.6 or higher
    Flask
    PyTube
    OpenAI API key


 ## Installation

Clone this repository:

	git clone https://github.com/YOUR_USERNAME/youtube-transcription-and-summarization.git


2. Install the required dependencies:

	pip install -r requirements.txt


## Running the application

1. Start the Flask application:

flask run
OR
	python app.py

## License

This project is licensed under the MIT License.

