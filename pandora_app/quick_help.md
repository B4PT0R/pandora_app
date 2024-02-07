Pandora is a Streamlit interface for the [pandora_ai](https://github.com/B4PT0R/pandora_ai) GPT4-console. It's both a fully working python console and a GPT4 assistant capable of running code, all wrapped up in a web interface thanks to Streamlit. It's main feature is to provide a special tool (a [st_stacker](https://github.com/B4PT0R/streamlit_stacker) object) declared as `st` in the console from which you may run streamlit commands interactively and render widgets in the chat dynamically (while it's running). The AI agent may as well interact with `st` to render any streamlit widget in the console, empowering it with rich output capabilities (TTS and STT, markdown, latex, plotting tools, dataframes, image/audio/video players, gui elements with callbacks, html/javascript iframes, or even custom react components) which offer a wide multimodal channel of interaction with the user.

The App is designed to be user-friendly yet as powerful as an AI python console can be.

## Working with Streamlit in Pandora

[Streamlit](https://streamlit.io/) is a user friendly yet powerful framework to generate interactive web apps using only python code. All Streamlit commands can be used directly in the Pandora console to render all kinds of interactive and programmable widgets (button, text input, slider, multiselector, pretty plots, data tables...) in the chat interface. Please refer to the [Streamlit documentation](https://docs.streamlit.io/library/api-reference) to get to know all the awesome widgets Streamlit features. 

One thing to keep in mind when using Streamlit commands in the Pandora console is that your scripts will run only once, therefore you can’t rely on a similar scripting logic as conventional Streamlit scripts relying on the script looping on itself : Namely, all interactivity must be implemented using callbacks.

Second thing to be aware of is that the console uses a special object (st_stacker) pre-declared as `st` to mimic the behavior of the streamlit module. You can use this module with similar commands and syntax as streamlit, with one minor change though : All widgets you will declare won’t output their state value directly, but an st_output placeholder object instead. This placeholder object has a .value property that will be updated in real time as soon as your widget is rendered and have a non-empty state.

Remember that the AI can help you at any time in case you have questions about the specific intergration of Streamlit in this console.

## Examples

Here are a few scripts to showcase how the integration of Streamlit works in the Pandora environment. Just copy/paste them in the console and run them to see the result (Ctrl+Enter to submit).

1. Show a text input and a button with callback to display the text content:

```python
txt=st.text_input("Enter text here:") # txt in not a string here, but an st_output object

def callback(txt):
    if txt.value:
        # Access the actualized value of the widget via the .value property
        st.write(f"You entered : {txt.value}") 

st.button("Click me", on_click=callback,args=(txt,))
```

2. Render an interactive plot with a slider:

```python
import numpy as np
import matplotlib.pyplot as plt

# Create a figure and axis object
fig, ax = plt.subplots()

# Initial plot
x = np.linspace(0, 1, 100)
ax.plot(x, x)

# Display the initial plot
st.pyplot(fig)

# Function to replot the graph
def replot():
    # Clear the current plot
    ax.clear()
    # Generate new x values
    x = np.linspace(0, 1, 100)
    # Get the current value of the slider
    n = slider.value
    # Plot the new data
    ax.plot(x, x**n)

# Create a slider widget
slider = st.slider('Select exponent', min_value=0.0, max_value=2.0, value=1.0, step=0.1, on_change=replot)
```

## Explanations and tips:

### Security 
Your account is managed via firebase authentication. Even as the admin, I don't have access to your password. Proper security rules are set in the firebase project to prevent anyone but you accessing your data.
### API keys 
All API keys needed to enable the AI features or other tools are transmitted and stored safely encrypted with your password in firebase. All efforts are made to ensure safe transmission and storage of sensitive data.
### Websearch
In order to enable the websearch tool of the AI agent, you may provide your google custom search API key and CX in the Settings page.
### Storage
All files you create during a session are dumped to firebase storage when you log out. It's therefore recommended that you log out gracefully to avoid your work being lost. To prevent unwanted data loss you may call the `dump_workfolder()` function at any time in the console to upload your files to the cloud storage. When using the web app, your user folder will be wiped from the app's file system once you log out. Your files will be uploaded again from firebase storage when you sign in.
### Stdin redirection
When using a python command that wants to read from `stdin` such as the `input` command, the script will pause and a special input widget will render to let you enter a string. This string will be available immediately when your script resumes execution (without requiring a rerun). You can therefore use the `input` command in your scripts seamlessly. 
### Shortcuts
Running `exit()` or `quit()` commands in the console will log you out gracefully. Running `clear()` in the console will clear the chat (This won't affect the python session and context memory of the AI agent).
### Restart session
You can restart the python session by clicking the 'Restart Session' button in the sidebar menu. This will also reinitialize the AI agent to its startup state. You can achieve a similar result by running `restart()` in the console.
### Editor
A text editor is provided within the app to enable opening and editing files. You may open it via the 'Open editor' button in the sidebar. Alternatively you may use the `edit` function directly from the console. `edit(file=your_file,text=your_text)` will open your file in the editor, prefilled with an optional string of text.
### Pandora as a python object
Pandora (the AI assistant) is declared as a python object in the console under the name `pandora`. You may thus interact with it programmatically.
### Observation
Pandora is equipped with a special `observe` tool enabling it to look at the content of any folder, file, data structure, image... When applied to a module, class or function this will inspect the object and access its documentation. You may thus ask Pandora to observe almost anything to get information about it, including the `pandora` object itself !
### Hybrid scripting
Pandora supports mixing both natural language and python code in the same input script. A parser determines which is which based on python syntactic correctness of each line. Natural language parts will be sent as prompts to the AI assistant and rendered as chat messages, the python code parts will be executed directly in the interpreter without triggering an assistant response. Beware that single word inputs like "Hello" will be interpreted as an attempt to access a variable by the parser and will most likely result in a "not defined" exception. To avoid this, you should use punctuation to help the parser understand your word is meant to be a message to the assistant: "Hello!" 
### Web scraping
Pandora comes equipped with a headless firefox webdriver in its toolkit. Useful to make it navigate through webpages, take webshots, interact with the DOM object, scrap data... You can use this web-driver yourself by running `driver=get_webdriver()`. In order to use it from the local client you should have firefox installed on you computer.
### LaTeX and PDF
The web-app comes equipped with a minimal LaTeX distribution enabling Pandora to use pdflatex to generate pdf documents from .tex files. A dedicated tool is declared in the console as `tex_to_pdf(tex_file,pdf_file)`. To be able to use it via the local app, you should have a LaTeX distribution and pdflatex installed on your computer. A custom streamlit widget enables displaying pdf files in the chat, you can use it via the `show_pdf(file_or_url)` shortcut.
### Memory
Pandora uses a `memory.json` file associated to your user profile for storing and remembering any kind of information across sessions. The assistant has permanent contextual visibility on the memory content. You can use it to guide the assistant towards the desired behavior, save user information, preferences or memos. Just ask Pandora and it will remember something durably.
### Startup
A `startup.py` file specific to your user profile will be executed whenever a new session starts. You may use it to pre-declare your favorite functions/tools to avoid having to declare them manually every new session. You may also use it to declare custom tools the agent will be able to use via the `pandora.add_tool` method. You will find the `memory.json` and `startup.py` files in the `config` folder of your workfolder. Feel free to edit them with the built-in editor.

