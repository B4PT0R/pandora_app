
# Pandora Virtual Assistant

Pandora is an advanced AI Python console, resulting from the combination of the latest GPT-4 Turbo model from OpenAI and an interactive Python interpreter supporting Streamlit commands. This console allows users to execute Python commands/scripts in real time like a conventional Python console, but also allows to interact in natural language with the assistant and offers rich interactive and multimodal capabilities based on the real-time execution of AI-generated python scripts.

## Main Features

- **Python Console**: Execute Python commands/scripts in real time as in a conventional Python console, the AI can help you in your workflow at any time thanks to its continuous observation of the session.

- **Multilingual**: Interact with the assistant in many languages thanks to its processing and speech synthesis capabilities.

- **File/Image Analysis**: Transmit files or images for analysis.

- **Dynamic Streamlit Interface and Interactive Widgets**: You or the AI can use the full range of Streamlit commands via the console to generate widgets in the chat interface, creating a dynamic and rich user experience.

- **Image Generation**: Create images from textual descriptions.

- **LaTeX to PDF Conversion**: Generation of aesthetic documents via the conversion of .tex files into PDF documents.

- **Web Search**: Perform web searches and read the content of web pages.

- **Cloud storage**: Acces your files and preferences from anywhere thanks to cloud storage of your user folder.

## Installation

Clone this repository to a local folder. cd to this folder and run:

```bash
$ pip install -r requirements.txt
```

Alternatively you may use the web-app here

## Usage

In the same folder, run:
```
$ sh pandora.sh
```
The app will start a local webserver and launch in your default webbrowser.

The app is local and runs python code locally on your system, but user settings and cloud storage are managed via a cloud provider.

You will thus need to create an account and authenticate to use the app.

Register your OpenAI API key to enjoy all the AI features (Your API key will be kept safely encrypted in your user profile).

That's it, you can start typing your python commands or interact with Pandora in natural language via the input cell.

## Use Cases

- **Python Programming Learning**: Use Pandora to learn Python with interactive examples and real-time explanations.

- **Data Analysis, Python Development, or Research Assistance**: Take advantage of Pandora's expertise to analyze data, write scripts, or perform complex research.

- **Automatic Document/Image Generation**: Ask Pandora to generate documents or images based on textual descriptions.

- **Web Content Search and Extraction**: Use Pandora to find information on the Internet and extract it for later use.

- **Educational or Professional Project Development**: Integrate Pandora into your projects to provide an interactive and enriching experience.

- **Multimedia Assistance**: Use Pandora's multimodal capabilities to analyze and generate multimedia content.

- **Decision Support / Brainstorming**: Benefit from the AI's vast knowledge as well as its data analysis capabilities to stay informed and make enlightened decisions.

- **Interactive Content Creation**: Create tutorials, demonstrations, or interactive presentations with Streamlit widgets.


## License

This project is licensed. Please see the LICENSE file for more details.

## Contributions

Contributions are welcome. Please open an issue or a pull request to suggest changes or additions.

## Contact

For any questions or support requests, please contact Baptiste Ferrand at the following address: bferrand.maths@gmail.com.
