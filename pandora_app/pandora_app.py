import os,sys
_root_=os.path.dirname(os.path.abspath(__file__))
os.environ['ROOT_PATH']=_root_
def root_join(*args):
    return os.path.join(_root_,*args)

if not sys.path[0]==_root_:
    sys.path.insert(0,_root_)

from tools.restrict_module import restrict_module
from tools.crypto import encrypt,decrypt
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_stacker import st_stacker
from pandora_ai import Pandora, NoContext, Message
from tools.tex_to_pdf import tex_to_pdf
from tools.custom_code_editor import editor, ext_to_lang
from streamlit_input_box import input_box
from tools.whisper_stt import whisper_stt
from streamlit_TTS import openai_text_to_audio,auto_play
from firebase_user import FirebaseClient
from objdict_bf import objdict
import shutil
import time

if not os.path.isdir(root_join("UserFiles")):
    os.mkdir(root_join("UserFiles"))

#------------------------shortcuts--------------------------

state=st.session_state

def user_join(*args):
    return os.path.join(state.user_folder,*args)

#-------------Initialize session_state variables--------------

def initialize_state(state):

    if 'mode' not in state:
        if _root_.startswith('/mount') or _root_.startswith('/app'):
            Pandora.setup_folder(root_join("UserFiles"))
            state.mode="web"
        else:
            Pandora.setup_folder()
            state.mode="local"

    if not 'firebase' in state:
        config=objdict.load(root_join("app_config.json"))
        state.firebase=FirebaseClient(config)

    if not 'user_data' in state:
        state.user_data=None

    #Password
    if 'password' not in state:
        state.password=None

    if 'config' not in state:
        state.config=objdict.load(root_join(".streamlit","config.toml"),_backend='toml')

    if 'needs_rerun' not in state:
        state.needs_rerun=False

    if 'page' not in state:
        state.page="login"

    #A boolean indicating if the user's session has been initialized
    if 'session_has_initialized' not in state:
        state.session_has_initialized=False

    #A boolean indicating if the user has log-out
    if 'log_out' not in state:
        state.log_out=False

    #User folder
    if 'user_folder' not in state:
        state.user_folder=""

    #Main streamlit commands stacker for the console queue (allows using streamlit commands directly in the input cell)
    if 'stacker' not in state:
        state.stacker=st_stacker(mode='streamed')

    #the AI assistant. Initialized at user login.
    if 'agent' not in state:
        state.agent=None

    #A variable allowing access to the chat container from anywhere
    if 'chat' not in state:
        state.chat=None

    #The current key of the editor ace widget
    if 'editor_key' not in state:
        state.editor_key = state.stacker.key_manager.gen_key()

    #the file currently open in the editor
    if 'open_file' not in state:
        state.open_file=None

    #the content of the file currently open in the editor
    if 'file_content' not in state:
        state.file_content=None

    #whether to show the editor or not
    if 'show_editor' not in state:
        state.show_editor=False

initialize_state(state)
stk=state.stacker
stk.reset()
stk.mode='streamed'

#------------------------------Main functions-------------------------------------

def terminate_streamlit_server():
    import signal
    id = os.getpid()
    os.kill(id, signal.SIGTERM)

def log_out():
    state.log_out=True
    state.needs_rerun=True

def avatar(role):
    if role=='assistant':
        return root_join("app_images","pandora-avatar.png")
    elif role=="user":
        return root_join("app_images","user-avatar.png")
    elif role=="system":
        return root_join("app_images","system-avatar.png")

def langs():
    from gtts.lang import tts_langs
    return list(tts_langs())

#Restarts the whole session to startup state
def restart():
    stk.clear()
    init_pandora()
    state.needs_rerun=True
        
#Clears the console's queue
def clear():
    stk.clear()
    state.needs_rerun=True

def prepare_user_folder():
    state.user_folder=Pandora.folder_join(state.user_data.name)
    if not os.path.exists(state.user_folder):
        os.mkdir(state.user_folder)
    state.firebase.storage.load_folder(state.user_folder)

def load_user_data():
    data=state.firebase.firestore.get_user_data().copy()
    for key in ["openai_api_key","google_search_api_key","google_search_cx"]:
        if data.get(key):
            data[key]=decrypt(data[key],state.password)
    state.user_data=data

def dump_user_data():
    data=state.user_data.copy()
    for key in ["openai_api_key","google_search_api_key","google_search_cx"]:
        if data.get(key):
            data[key]=encrypt(data[key],state.password)
    state.firebase.firestore.set_user_data(data)

def dump_user_folder():
    state.firebase.storage.dump_folder(state.user_folder)

#Save the content of the editor as... 
def save_as(file):
    with open(file,'w') as f:
        f.write(state.file_content)
    state.open_file=file

#Closes the editor
def close_editor():
    state.show_editor=False

#Runs the code content open in the editor in the console  
def run_editor_content():
    code=state.file_content
    with state.chat:
        state.agent(code)
    state.needs_rerun=True

#Opens a new buffer or file in the editor (prefilled with an optional text)
def edit(file='buffer',text=None,wait=False):
    state.show_editor=True
    state.open_file=file
    if not file=='buffer':
        if text is None:
            if not os.path.exists(file):
                file_content=""
            else:
                with open(file,'r') as f:
                    file_content=f.read()
        else:
            file_content=text
    else:
        if text is None:
            file_content=''
        else:
            file_content=text
    state.file_content=file_content
    
#---------------------------------App layout-------------------------------------

#Sets the sidebar menu
def make_menu():
   with st.sidebar:

        st.subheader("Session")
        st.text(state.user_data.name)
        def on_log_out_click():
            state.log_out=True
        st.button("Log out",on_click=on_log_out_click,use_container_width=True)
        st.write('---')

        st.subheader("Quick settings")

        def on_enabled_change():
            state.agent.config.enabled=state.enabled
        st.toggle("Assistant enabled",value=state.agent.config.enabled,on_change=on_enabled_change,key='enabled')

        def on_voice_enabled_change():
            state.agent.config.voice_enabled=state.voice_enabled
        st.toggle("Voice enabled",value=state.agent.config.voice_enabled,on_change=on_voice_enabled_change,key='voice_enabled')

        def on_lang_change():
            state.user_data.language=state.language
            state.agent.config.language=state.language
            dump_user_data()
        st.selectbox("Language:",index=langs().index(state.user_data.language),options=langs(),on_change=on_lang_change,key='language')

        def on_restart_click():
            restart()
        st.button("Restart session",on_click=on_restart_click,use_container_width=True)

        def on_settings_click():
            state.page='settings'
        st.button("Settings",on_click=on_settings_click,use_container_width=True)

        def on_editor_click():
            edit('buffer')
        st.button("Open editor",on_click=on_editor_click,use_container_width=True)

        def on_help_click():
            state.page='help'

        st.button("About / Help",on_click=on_help_click,use_container_width=True)

def make_sign_up():
    def on_submit_click():
        if state.sign_up_username and state.sign_up_email and state.sign_up_password and state.sign_up_confirm_password:
            if len(state.sign_up_password)>=8:
                if state.sign_up_password==state.sign_up_confirm_password:
                    try:
                        state.firebase.auth.sign_up(state.sign_up_email,state.sign_up_password)
                    except Exception as e:
                        st.warning(f"Error: {e.message}")
                    else:
                        state.password=state.sign_up_password
                        state.user_data=objdict(
                            name=state.sign_up_username,
                            openai_api_key=None,
                            google_search_api_key=None,
                            google_search_cx=None,
                            made_api_key_choice=False,
                            language='en'
                        )
                        dump_user_data()
                        state.needs_rerun=True
                else:
                    st.warning("Your password doesn't match its confirmation.")
            else:
                st.warning("Your password should be at least 8 characters long.")                   
        else:
            st.warning("Non-empty username, email and password required.")

    with st.form("sign_up",clear_on_submit=True):
        st.text_input("Username:",key='sign_up_username')
        st.text_input("Email:",key='sign_up_email')
        st.text_input("Password (at least 8 characters long):",type="password",key='sign_up_password')
        st.text_input("Confirm password:",type="password",key='sign_up_confirm_password')
        st.form_submit_button("Submit",on_click=on_submit_click)

def make_sign_in():
    def on_submit_click():
        if state.sign_in_email and state.sign_in_password:
            try:
                state.firebase.auth.sign_in(state.sign_in_email,state.sign_in_password)
            except Exception as e:
                st.warning(f"Error: {e.message}")
            else:
                state.password=state.sign_in_password
                load_user_data()
                state.needs_rerun=True                  
        else:
            st.warning("Non-empty username and password required.")

    with st.form("login",clear_on_submit=True):
        st.text_input("E-mail:",key='sign_in_email')
        st.text_input("Password:",type="password",key='sign_in_password')
        st.form_submit_button("Submit",on_click=on_submit_click)

#Makes the webapp login page        
def make_login():
    _,c,_=st.columns([30,40,30])
    with c:
        st.image(root_join("app_images","pandora_logo.png"))

    title_html = f"""
    <div style="
        background-color: {state.config.theme.backgroundColor};
        text-align: center;
        ">
        <h1 style="color: {state.config.theme.primaryColor}; margin-bottom: 0;">Pandora</h1>
        <hr style="border: 1px solid {state.config.theme.primaryColor}; margin: 5px auto; width: 50%;" />
        <p style="color: {state.config.theme.primaryColor}; margin-top: 0;">OpenAI + Streamlit powered Python console</p>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    tab1,tab2=st.tabs(["Sign-in","Sign-up"])
    with tab1:
        make_sign_in()
    with tab2:
        make_sign_up()

    if state.mode=="local":
        def on_goodbye():
            state.page="goodbye"
            state.needs_rerun=True

        _,a,_=st.columns([30,40,30])
        with a:
            st.button("Close Streamlit local server",on_click=on_goodbye,use_container_width=True)

def make_settings():
    def on_submit():
        st.success("Settings saved")
        if state.username_input:
            state.user_data.name=state.username_input
            state.agent.config.username=state.username_input
        if state.openai_api_key_input:
            state.user_data.openai_api_key=state.openai_api_key_input
        if state.google_search_api_key_input:
            state.user_data.google_search_api_key=state.google_search_api_key_input
        if state.google_search_cx_input:
            state.user_data.google_search_cx=state.google_search_cx_input
        if state.select_lang:
            state.user_data.language=state.select_lang
            state.agent.config.language=state.select_lang
        
        dump_user_data()
        state.page="default"
        state.needs_rerun=True

    with st.form("settings"):
        st.subheader("Settings")
        st.write("Your username (How Pandora should call you):")
        st.text_input("Username",value=state.user_data.get('name'),key='username_input')
        st.write("OpenAI API key used to power the AI assistant:")
        st.text_input("OpenAI API key",value=state.user_data.get('openai_api_key'),key='openai_api_key_input')
        st.write("Google custom search credentials (used to enable the websearch tool):")
        st.text_input("Google custom search API key",value=state.user_data.get('google_search_api_key'),key='google_search_api_key_input')
        st.text_input("Google custom search CX",value=state.user_data.get('google_search_cx'),key='google_search_cx_input')
        st.write("Default language:")
        st.selectbox("Language",index=langs().index(state.user_data.language),options=langs(),key='select_lang')
        st.form_submit_button("Save settings",on_click=on_submit)

def make_OpenAI_API_request():
    st.subheader("OpenAI API key")
    st.write("To interact with Pandora (the AI assistant) and enjoy voice interaction, you need to provide a valid OpenAI API key. This API key will be stored safely encrypted in your user profile. If you don't provide any, Pandora will still work as a mere python console, but without the possibility to interact with the assistant. In case you chose not to, you will still be able to register your API key at any time via the Settings page accessible from the sidebar.")
    def on_submit():
        if state.openai_api_key_input:
            state.user_data.openai_api_key=state.openai_api_key_input
        state.user_data.made_api_key_choice=True
        dump_user_data()
        state.needs_rerun=True
        
    with st.form("OpenAI_API_Key",clear_on_submit=True):
        st.text_input("Please enter your OpenAI API key (leave blank if you don't want to):",type="password",key="openai_api_key_input")
        st.form_submit_button("Submit",on_click=on_submit)

def make_help():
    _,c,_=st.columns([30,40,30])
    with c:
        st.image(root_join("app_images","pandora_logo.png"),use_column_width=True)

    title_html = f"""
    <div style="
        background-color: {state.config.theme.backgroundColor};
        text-align: center;
        ">
        <h1 style="color: {state.config.theme.primaryColor}; margin-bottom: 0;">Pandora</h1>
        <hr style="border: 1px solid {state.config.theme.primaryColor}; margin: 5px auto; width: 50%;" />
        <p style="color: {state.config.theme.primaryColor}; margin-top: 0;">OpenAI + Streamlit powered Python console</p>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    with open(root_join("quick_help.md"),'r') as f:
        quick_help=f.read()
    st.write(quick_help)

    def on_ok_click():
        state.page="default"

    _,d,_=st.columns([30,40,30])
    with d:
        st.button("OK", on_click=on_ok_click,use_container_width=True)

def make_chat():

    _,c,_=st.columns([15,70,15])
    with c:
        st.image(root_join("app_images","pandora_logo.png"),use_column_width=True)

    state.chat=st.container()

    with state.chat:
        stk.refresh()

    text=input_box(just_once=True,min_lines=1,max_lines=100,key='text')
    a,b=st.columns(2)
    with a:
        voice=whisper_stt(openai_api_key=state.user_data.openai_api_key,start_prompt="Talk to Pandora",use_container_width=True,language=state.user_data.language,just_once=True,key='voice')
    with b:
        drop_file=st.button("Drop a file",use_container_width=True)

    if drop_file:
        def on_file_change():
            file=state.file
            state.agent.upload_file(bytesio=file)
            stk.mode='static'
            with state.chat:
                stk.success(f"{file.name} successfully uploaded.")
            stk.mode='streamed'

        st.file_uploader("Choose a file:",key='file',on_change=on_file_change)

    prompt=text or voice

    if prompt:
        with state.chat:
            state.agent(prompt)

#Displays the editor
def make_editor():
    st.subheader(f"Editing: {os.path.basename(state.open_file)}")
    ext=os.path.splitext(state.open_file)[1]
    lang=ext_to_lang(ext)
    empty=st.empty()
    event,state.file_content=editor(state.file_content,lang=lang,key=state.editor_key)
    if event=="close":
        close_editor()
        state.needs_rerun=True
    elif event=="open":
        def on_file_name_change():
            if not state.file_name==' ':
                state.editor_key=state.stacker.key_manager.gen_key()
                edit(user_join(state.file_name))
        def get_relative_paths(folder_path):
            """Get all relative paths of files in the given folder, recursively."""
            relative_paths = []
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    rel_dir = os.path.relpath(dirpath, folder_path)
                    rel_path = os.path.join(rel_dir, filename)
                    if rel_path.startswith('./'):
                        rel_path=rel_path[2:]
                    relative_paths.append(rel_path)
            return relative_paths
        files = [' ']+get_relative_paths(state.user_folder)
        with empty:
            st.selectbox('Select a file:',files,on_change=on_file_name_change,index=0,key='file_name')
    elif event=="delete":
        def on_yes():
            os.remove(state.open_file)
            state.editor_key=state.stacker.key_manager.gen_key()
            edit()
            with empty:
                st.success("File deleted.")
        with empty:
            st.selectbox('Are you sure you want to delete this file ?',['No','Yes'],on_change=on_yes,index=0,key='sure')  
    elif event=="new":
        state.editor_key=state.stacker.key_manager.gen_key()
        edit()
        state.needs_rerun=True
    elif event=="submit":
        if not state.open_file=='buffer':
            save_as(state.open_file)
            with empty:
                st.success("File saved.")
        else:
            def on_file_name_change():
                save_as(user_join(state.file_name))
                with empty:
                    st.success("File saved.")
            with empty:
                st.text_input("Enter name of file:",on_change=on_file_name_change,key='file_name')
    elif event=="save_as":
        def on_file_name_change():
            save_as(user_join(state.file_name))
            with empty:
                st.success("File saved.")
        with empty:
            st.text_input("Enter name of file:",on_change=on_file_name_change,key='file_name')
    elif event=="rename":
        def on_file_name_change():
            os.remove(state.open_file)
            save_as(user_join(state.file_name))
            with empty:
                st.success("File renamed.")
        with empty:
            st.text_input("Enter new name of file:",on_change=on_file_name_change,key='file_name')
    elif event=="run":
        run_editor_content()

def init_pandora():

        def text_to_audio(text,language=None):
            return openai_text_to_audio(text=text,openai_api_key=state.user_data.openai_api_key,language=language)

        def input_hook():
            txt=stk.modal_input(firebase_client=state.firebase)
            return txt.value

        def display_hook(content,tag,status):
            if tag in ['user_message','assistant_message']:
                stk.write(content)
            elif tag in ['user_code']:
                stk.code(content, language='python')
            elif tag in ['interpreter']:
                stk.code(content,language='text')
            elif tag in ['status']:
                if not content=="#DONE#":
                    status.value.update(label=content,state="running")
                else:
                    status.value.update(state="complete")
            else:
                pass

        def context_handler(message):
            if message.tag in ['user_message','assistant_message','user_code','interpreter']:
                with stk.chat_message(name=message.role,avatar=avatar(message.role)):
                    e=stk.empty()
                return e
            elif message.tag in ['status']:
                status=stk.status(label='Done',state="complete")
                return status
            else:
                return NoContext()

        preprompt="""
        The chat/console in which you currently interact with the user is a streamlit app. 
        Thanks to the 'st' helper object (an st_stacker object), the python console supports streamlit commands and the display of widgets in the chat.
        This is made possible by stacking the streamlit calls you make in your scripts and resolve the stack every rerun in the streamlit app's main script.
        Due to this peculiar implementation, outputs of widgets are st_output placeholder object. 
        Their .value attribute will be updated in real time as soon as the widget is rendered and has a non-empty state. 
        You must therefore always use this attribute when accessing values of widgets.
        Remember also that scripts run only once in this console setting. 
        Conventional streamlit scripting logic, relying on the script looping on itself, is not possible here. 
        You must therefore implement all the interactive logic of widgets using functions passed as callbacks.
        example: 
            def on_click():
                st.write("You entered: "+txt.value)

            txt=st.text_input("Enter text here:")
            st.button("click me!",on_click=on_click)

        Use streamlit features as your primary way to display images, videos, audio, plots, forms, dataframes and other interactive elements in the chat.
        Worth mentioning, stdin is redirected to a custom modal input widget, thus allowing to use standard python 'input' command seamlessly.
        """
        replacements=[
            ('import streamlit as st',''),
            ('plt.show()','st.pyplot(plt.gcf())'),
            ('st.pyplot(plt)','st.pyplot(plt.gcf())'),
            ('st.pyplot()','st.pyplot(plt.gcf())'),
            ]
        env="User's local system" if state.mode=='local' else "Streamlit cloud server"
        infos=[
            f"Code execution environment: {env}",
            "The user's OpenAI api key (and other secrets) necessary to make you and your tools function are all stored safely encrypted in the users database."
            "clear() will clear the chat (wipe all messages and widgets from the st_stacker's stack). Context memory will remain.",
            "exit() or quit() will end the session and log the user out gracefully.",
            "restart() will restart the whole python session (including the AI assistant) to its startup state.",
            "dump_workfolder() will dump the whole user folder to cloud storage."
        ]
        builtin_tools=['observe','generate_image','memory','websearch','get_webdriver','retriever']
        state.agent=Pandora(openai_api_key=state.user_data.openai_api_key,google_custom_search_api_key=state.user_data.google_search_api_key,google_custom_search_cx=state.user_data.google_search_cx, work_folder=state.user_folder,builtin_tools=builtin_tools,preprompt=preprompt,infos=infos,input_hook=input_hook,display_hook=display_hook,context_handler=context_handler,text_to_audio_hook=text_to_audio,audio_play_hook=auto_play,thread_decorator=add_script_run_ctx)
        state.stacker.set_current_code_hook(state.agent.console.get_current_code)
        state.agent.config.update(
            voice_enabled=False,
            username=state.user_data.name,
            code_replacements=replacements,
            language=state.user_data.language,
            model='gpt-4-vision-preview',
            vision=True,
            display_mode="cumulative"
        )
        state.agent.console.update_namespace(
            clear=clear,
            exit=log_out,
            quit=log_out,
            restart=restart,
            dump_workfolder=dump_user_folder,
        )

        state.agent.add_tool(
            name='st',
            description="st # A streamlit stacker object. Use it just like the streamlit module to render widgets in the chat.",
            obj=state.stacker,
            type="object"
        )

        state.agent.add_tool(
            name='tex_to_pdf',
            obj=tex_to_pdf,
            description='tex_to_pdf(tex_file,pdf_file) # Converts a .tex file to a pdf document. Use it as a default way to generate pdf documents.',
            parameters={
                'tex_file':'path of the source tex file.',
                "pdf_file":"chosen path for destination pdf"
            },
            required=['tex_file','pdf_file']
        )

        def show_pdf(source):
            stk.pdf(source)

        state.agent.add_tool(
            name='show_pdf',
            description="show_pdf(path_or_url) # Display a pdf document in the chat interface.",
            obj=show_pdf
        )
        

        def pandora_edit(*args,**kwargs):
            edit(*args,**kwargs)
            state.needs_rerun=True

        state.agent.add_tool(
            name='edit',
            description="edit(file='buffer',text=None) # Opens a buffer or file in the default text editor widget to let the user visualize and edit it, prefilled with an optional string of text.",
            obj=pandora_edit,
            parameters=dict(
                file="(path) The file to open in the editor widget, defaults to 'buffer' to open an unnamed buffer.",
                text="(string) The string of text used to prefill the editor's text content. defaults to None."
            ),
            example="""
            edit() # will open a new empty buffer
            edit(file="my_file.txt") # will open the file in the editor
            edit(text="my_string") # will open a buffer prefilled with the text string
            edit(file="my_file.txt",text="my_string") # will open the file and overwrite the content with the text string
            """,
            required=[]
        )

#Initialize the user's session
def initialize_session():
    #Initialize the user's session
    st.subheader("Initializing your session.")
    with st.spinner("Please wait..."): 
        prepare_user_folder()
        init_pandora()
        state.session_has_initialized=True
        state.needs_rerun=True
        state.page="default"

def do_log_out():
    st.subheader("Logging you out of your session.")
    with st.spinner("Please wait..."):
        dump_user_data()
        state.firebase.storage.dump_folder(state.user_folder)
        state.firebase.auth.log_out()
        if state.mode=='web':
            shutil.rmtree(state.user_folder)
        state.open_file=None
        state.file_content=None
        state.show_editor=False
        state.user_data=None
        state.password=""
        state.user_folder=""
        state.stacker.clear()
        state.log_out=False
        state.agent=None
        state.session_has_initialized=False
        state.needs_rerun=True

def make_goodbye():
    def text_with_css(text, **kwargs):
        # Construction de la chaîne de style CSS à partir des kwargs
        css_style = "; ".join(f"{key.replace('_', '-')}: {value}" for key, value in kwargs.items())
        # Utilisation de st.markdown pour insérer le texte dans un div avec style personnalisé
        st.markdown(f"<div style='{css_style}'>{text}</div>", unsafe_allow_html=True)
    text_with_css(
        "Local Streamlit server closed",
        text_align="center",
        color="#67b5f9",
        border="2px solid #67b5f9",
        border_radius="10px",
        padding="20px",
        margin="100px auto",  # auto for horizontal centering, 100px for vertical space
        font_size="24px"
    )
    time.sleep(1)
    terminate_streamlit_server()
    st.stop()

#-----------------------------Main app session's logic-------------------------

if state.page=="goodbye":
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    make_goodbye()
elif not state.firebase.auth.authenticated:
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    #Ask for credentials
    make_login()
elif not state.user_data.get('openai_api_key') and not state.user_data.made_api_key_choice:
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    make_OpenAI_API_request()
elif not state.session_has_initialized:
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    #Initialize the session
    initialize_session()
elif state.log_out:
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    do_log_out()
elif state.page=="settings":
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    make_settings()
elif state.page=='help':
    st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
    make_help()
else:
    #Show the app's main page
    if state.show_editor:
        st.set_page_config(layout="wide",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
        make_menu()
        console_column,editor_column=st.columns(2)
        with console_column:
            make_chat()
        with editor_column:
            make_editor()
    else:
        st.set_page_config(layout="centered",page_title="Pandora",page_icon=root_join("app_images","pandora_logo.png"),initial_sidebar_state="collapsed")
        make_menu()
        make_chat()

stk.mode='static'

if state.needs_rerun:
    state.needs_rerun=False
    st.rerun()
    