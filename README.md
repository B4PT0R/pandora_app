
# Pandora App

Pandora App is a Streamlit interface for the [pandora_ai](https://github.com/B4PT0R/pandora_ai) GPT4-console. It's both a fully working python console and a GPT4 assistant capable of running code, all wrapped up in a web interface thanks to Streamlit. It's main feature is to provide a special tool (a [st_stacker](https://github.com/B4PT0R/streamlit_stacker) object) to run streamlit commands live from the interactive console and render widgets in the chat dynamically (from the app while it's running). This tool is also passed to the AI agent which may thus interact with it to render any streamlit widget in the console. The AI is thus empowered with super rich output capabilities (TTS and STT, markdown, latex, plotting tools, dataframes, image/audio/video players, gui elements with callbacks, html/javascript iframes, custom react components) which offer a wide multimodal channel of interaction with the user.

The App is designed to be user-friendly yet as powerful as an AI python console can be.

## Main Features

- **Python Console**: Execute Python commands/scripts in real time as in a conventional Python console, the AI can help you in your workflow at any time thanks to its continuous observation of the session and its capacity to generate and run scripts. You can even mix natural language sentences with segments of python code in the same input script!

- **Multilingual**: Interact with the assistant in many languages thanks to its speech recognition and vocal synthesis capabilities (OpenAI).

- **Data/File/Image Analysis**: Transmit files or images for analysis. The Agent can observe text, files, data structures, python objects and modules (for documentation and inspection), as well as images thanks to its vision feature.

- **Dynamic Streamlit Interface and Interactive Widgets**: You or the AI can use the full range of Streamlit commands via the console to generate widgets in the chat interface in real time.

- **Image Generation**: Create images from textual descriptions with DALL-e 3.

- **LaTeX to PDF Conversion**: Generation of aesthetic documents via the conversion of .tex files into PDF documents and display them in a pdf reader.

- **Web search and scraping**: Perform web searches and read the content of web pages,or use a preimplemented selenium webdriver to interact, take webshots or extract data from webpages.

- **Personal folder/Cloud storage**: Acces your files and preferences from anywhere thanks to cloud storage of your user folder.

## Installation

Local installation:
```bash
$ pip install pandora-app
```

Alternatively you may use the web-app [here](https://pandora-ai.streamlit.app/)

## Usage

open a terminal and run :

```
$ pandora
```

The app will start a local webserver and launch in your default webbrowser.

The app is local and runs python code locally on your system, but user settings and cloud storage are managed via a cloud provider.

You will thus need to create an account and authenticate to use the app.

Register your OpenAI API key to enjoy all the AI features (Your API key can be entered from the app, provided from your system as an environment variable or can be kept safely encrypted in your user profile within the database so that you may use pandora from anywhere, including from your smartphone thanks to the Streamlit cloud version of the app).

That's it, you can start typing your python commands or interact with Pandora in natural language via the input cell.

## Use Cases

- **Python Programming Learning**: Use Pandora to learn Python with interactive examples and real-time explanations.

- **Data Analysis, Python Development, or Research Assistance**: Take advantage of Pandora's expertise to analyze data, write scripts, or perform complex research.

- **Automatic Document/Image Generation**: Ask Pandora to generate documents or images based on textual descriptions.

- **Web Content Search and Extraction**: Use Pandora to find information on the Internet and extract it for later use.

- **Modular use of custom tools you provide to the AI**: Pass the AI any new tool to play with (custom functions, python objects, APIs,...)

- **Productivity assistant**: Benefit from the AI's vast technical knowledge, data analysis capabilities, and long lasting memory to manage and speed up complex projects.

- **Interactive Content Creation**: Ask the assistant to help you create code, documentation, tutorials, demonstrations, beautiful logos or images, or intractive presentations using Streamlit widgets.


## License

This project is licensed. Please see the LICENSE file for more details.

## Contributions

Contributions are welcome. Please open an issue or a pull request to suggest changes or additions.

## Contact

For any questions or support requests, please contact Baptiste Ferrand at the following address: bferrand.maths@gmail.com.
