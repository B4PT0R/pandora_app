import os,sys
_root_=os.path.dirname(os.path.abspath(__file__))
def root_join(*args):
    return os.path.join(_root_,*args)

if not sys.path[0]==_root_:
    sys.path.insert(0,_root_)

from tools.restrict_module import restrict_module
from tools.crypto import encrypt,decrypt,gen_lock, check_lock
import streamlit as st
from streamlit_stacker import st_stacker
from pandora_ai import Pandora
from pandora_ai.pandora_agent import NoContext
from tools.tex_to_pdf import tex_to_pdf
from streamlit_input_box import input_box
from tools.whisperSTT import WhisperSTT
from streamlit_TTS import openai_text_to_audio,auto_play
from objdict_bf import objdict
import shutil
import time
import json
import io

if not os.path.isfile(root_join("users.json")):
    with open(root_join("users.json"),'w') as f:
        json.dump({},f)

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
            state.mode="web"
        else:
            state.mode="local"

    #Username
    if 'user' not in state:
        state.user=None

    #Password
    if 'password' not in state:
        state.password=None

    if 'authenticated'not in state:
        state.authenticated=False

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

    if 'language' not in state:
        state.language='fr'

    #A variable allowing access to the chat container from anywhere
    if 'chat' not in state:
        state.chat=None


initialize_state(state)
stk=state.stacker
stk.reset()

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
        return root_join("app_images/pandora-avatar.png")
    elif role=="user":
        return root_join("app_images/user-avatar.png")
    elif role=="system":
        return root_join("app_images/system-avatar.png")

def langs():
    from gtts.lang import tts_langs
    return list(tts_langs())

#Restarts the whole session to startup state
def restart():
    stk.clear()
    if not state.openai_api_key=="":
        init_pandora()
        

#Clears the console's queue
def clear():
    stk.clear()
    state.needs_rerun=True


def prepare_user_folder():
    if not os.path.exists(state.user_folder):
        os.mkdir(state.user_folder)
    
#---------------------------------App layout-------------------------------------

#Sets the sidebar menu
def make_menu():
   with st.sidebar:

        st.subheader("Session")
        st.text(state.user)
        def on_log_out_click():
            state.log_out=True
        st.button("Log out",on_click=on_log_out_click,use_container_width=True)
        st.write('---')

        st.subheader("Quick settings")

        def on_enabled_change():
            state.agent.config.enabled=state.enabled
        st.toggle("Assistant enabled",value=state.agent.config.enabled,on_change=on_enabled_change,key='enabled')

        def on_voice_mode_change():
            state.agent.config.voice_mode=state.voice_mode
        st.toggle("Voice enabled",value=state.agent.config.voice_mode,on_change=on_voice_mode_change,key='voice_mode')

        def on_lang_change():
            state.agent.config.language=state.language
        st.selectbox("Language:",index=langs().index(state.agent.config.language),options=langs(),on_change=on_lang_change,key='language')

        def on_restart_click():
            restart()
        st.button("Restart session",on_click=on_restart_click,use_container_width=True)

        def on_settings_click():
            state.page='settings'
        st.button("Settings",on_click=on_settings_click,use_container_width=True)

def make_sign_up():
    def on_submit_click():
        if not state.sign_up_username=="" and not state.sign_up_password=="" and not state.sign_up_confirm_password=="" and state.sign_up_password==state.sign_up_confirm_password:
            try:
                users=objdict.load(root_join("users.json"))
                if not state.sign_up_username in users:
                    state.user=state.sign_up_username
                    state.password=state.sign_up_password
                    state.openai_api_key=None
                    users[state.user]={
                        'password':gen_lock(state.password,30),
                        'OpenAI_API_key':None
                    }
                    users.dump()
                    state.authenticated=True 
                    state.needs_rerun=True 
                else:
                    st.warning("This username / email adress is already taken.")
                
            except Exception as e:
                st.exception(e)
                st.warning("Something went wrong. Please try again.")    
        else:
            st.warning("Non-empty username email and password required.")

    with st.form("sign_up",clear_on_submit=True):
        st.text_input("Username:",key='sign_up_username')
        st.text_input("Password:",type="password",key='sign_up_password')
        st.text_input("Confirm password:",type="password",key='sign_up_confirm_password')
        st.form_submit_button("Submit",on_click=on_submit_click)

def make_sign_in():
    def on_submit_click():
        if not state.sign_in_username=="" and not state.sign_in_password=="":
            try:
                users=objdict.load(root_join("users.json"))
                if state.sign_in_username in users:
                    if check_lock(state.sign_in_password,users[state.sign_in_username]['password']):
                        state.user=state.sign_in_username
                        state.password=state.sign_in_password
                        if users[state.user].get('OpenAI_API_key'):
                            state.openai_api_key=decrypt(users[state.user]['OpenAI_API_key'],state.password)
                        else:
                            state.openai_api_key=None
                        state.authenticated=True 
                        state.needs_rerun=True                  
                    else:
                        st.warning("Wrong password.")
                        time.sleep(0.5)
                else:
                    st.warning("This username doesn't exist in the database.")

            except Exception as e:
                st.exception(e)
                st.warning("Something went wrong. Please try again.")    
        else:
            st.warning("Non-empty username and password required.")

    with st.form("login",clear_on_submit=True):
        st.text_input("Username:",key='sign_in_username')
        st.text_input("Password:",type="password",key='sign_in_password')
        st.form_submit_button("Submit",on_click=on_submit_click)

#Makes the webapp login page        
def make_login():
    _,c,_=st.columns([30,40,30])
    with c:
        st.image(root_join("app_images/pandora_logo.png"))

    title_html = """
    <div style="
        background-color: #12161c;
        text-align: center;
        ">
        <h1 style="color: #67b5f9; margin-bottom: 0;">Pandora</h1>
        <hr style="border: 1px solid #67b5f9; margin: 5px auto; width: 50%;" />
        <p style="color: #67b5f9; margin-top: 0;">OpenAI + Streamlit powered Python console</p>
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
        time.sleep(2)
        state.page="default"
        state.needs_rerun=True

    with st.form("settings"):
        st.subheader("Settings")
        st.text_input("OpenAI API key",value=state.openai_api_key,key='API_input')
        from gtts.lang import tts_langs
        st.selectbox("Language",options=tts_langs().keys(),key='select_lang')
        st.checkbox('Speech mode',key='select_speech')
        st.form_submit_button("Save settings",on_click=on_submit)

def make_OpenAI_API_request():
    st.subheader("OpenAI API key")
    st.write("To interact with Pandora (the AI assistant) and enjoy voice interaction, you need to provide a valid OpenAI API key. This API key will be stored safely encrypted in a local database, in such a way that you only can use it. If you don't provide any, Pandora will still work as a mere python console, but without the possibility to interact with the assistant.")
    def on_submit():
        state.openai_api_key=state.openai_api_key_input
        users=objdict.load(root_join("users.json"))
        users[state.user].update({'OpenAI_API_key':encrypt(state.openai_api_key,key=state.password)})
        users.dump()
        state.needs_rerun=True
        
    with st.form("OpenAI_API_Key",clear_on_submit=True):
        st.text_input("Please enter your OpenAI API key (leave blank if you don't want to):",type="password",key="openai_api_key_input")
        st.form_submit_button("Submit",on_click=on_submit)

def make_chat():

    _,c,_=st.columns([15,70,15])
    with c:
        st.image(root_join("app_images/pandora_logo.png"),use_column_width=True)

    
    state.chat=st.container()

    with state.chat:
        stk.refresh()

    text=input_box(just_once=True,min_lines=1,max_lines=100,key='text')
    a,b=st.columns(2)
    with a:
        voice=WhisperSTT(openai_api_key=state.openai_api_key,start_prompt="Talk to Pandora",use_container_width=True,language=state.language,just_once=True,key='voice')
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

def init_pandora():

        def text_to_audio(text,language=None):
            return openai_text_to_audio(text=text,openai_api_key=state.openai_api_key,language=language)

        def input_hook():
            txt=stk.modal_input(firebase_credentials=dict(st.secrets["firebase_credentials"]),firebase_config=dict(st.secrets["firebase_config"]))
            return txt.value

        def display_hook(message,status):
            if message.tag in ['interpreter','user_code']:
                stk.text(message.content)
            elif message.tag in ['user_message']:
                stk.write(message.content)
            elif message.tag in ['assistant_message']:
                stk.write(message.content)
            elif message.tag in ['assistant_code']:
                with status:
                    stk.code(message.content)
            elif message.tag in ['status']:
                if not message.content=="#DONE#":
                    status.value.update(label=message.content,state="running")
                else:
                    status.value.update(state="complete")
            else:
                pass

        def context_handler(message):
            if message.tag in ['user_message','assistant_message','user_code','interpreter']:
                msg=stk.chat_message(name=message.role,avatar=avatar(message.role))
                return msg
            elif message.tag in ['status']:
                status=stk.status(label='Done',state="running")
                return status
            else:
                return NoContext()

        preprompt="""
        The chat/console in which you currently interact with the user is a streamlit app. 
        Thanks to the 'st' helper object (an st_stacker object), the python console supports streamlit commands and the display of widgets in the chat.
        This is made possible by stacking the streamlit calls you make in your scripts and resolve the stack in the streamlit app's main script.
        Due to this peculiar implementation, outputs of widgets are st_output placeholder object. 
        Their .value attribute will be updated in real time as soon as the widget is rendered and has a non-empty state. 
        You must therefore always use this attribute when accessing values of widgets.
        Remember also that your scripts will run only once. 
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
        infos=[
            "Code execution environment: User's local system",
            "The user's OpenAI api key (and other secrets) necessary to make you and your tools function are all stored safely encrypted in the users database."
            "clear() method clears the chat (wipes all messages and widgets from the st_stacker's stack). Context memory remains.",
            "exit() or quit() methods ends the session and logs the user out gracefully."
        ]
        builtin_tools=['message','codeblock','status','observe','generate_image']
        state.agent=Pandora(openai_api_key=state.openai_api_key,work_folder=state.user_folder,builtin_tools=builtin_tools,preprompt=preprompt,infos=infos,input_hook=input_hook,display_hook=display_hook,context_handler=context_handler,text_to_audio_hook=text_to_audio,audio_play_hook=auto_play)
        state.agent.config.update(
            voice_mode=False,
            username=state.user,
            code_replacements=replacements,
            language=state.language,
            model='gpt-4-vision-preview',
            vision=True
        )
        state.agent.console.update_namespace(
            clear=clear,
            exit=log_out,
            quit=log_out
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
        

        if state.mode=='local':

            def open_in_new_tab(url):
                import webbrowser
                webbrowser.open(url)

            state.agent.add_tool(
                name="open_in_new_tab",
                description="open_in_new_tab(file_or_url) # open any file or url in a new tab of the default webrowser. Used when there is no alternative to display/read some content directly in the chat.",
                obj=open_in_new_tab
            )


#Initialize the user's session
def initialize_session():
    #Initialize the user's session
    st.subheader("Initializing your session.")
    with st.spinner("Please wait..."):
        if state.user_folder=="":
            state.user_folder=root_join("UserFiles",state.user) 
        prepare_user_folder()
        os.chdir(state.user_folder)
        init_pandora()
        state.session_has_initialized=True
        state.needs_rerun=True
        state.page="default"

def do_log_out():
    st.subheader("Login out of your session.")
    with st.spinner("Please wait.."):
        state.authenticated=False
        state.user=""
        state.password=""
        state.openai_api_key=None
        state.user_folder=""
        state.stacker.clear()
        state.log_out=False
        state.agent=None
        state.session_has_initialized=False
        state.needs_rerun=True
        time.sleep(2)

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

st.set_page_config(layout="centered",page_title="Pandora",initial_sidebar_state="collapsed")

if state.page=="goodbye":
    make_goodbye()
elif not state.authenticated:
    #Ask for credentials
    make_login()
elif state.openai_api_key is None:
    make_OpenAI_API_request()
elif not state.session_has_initialized:
    #Initialize the session
    initialize_session()
elif state.log_out:
    do_log_out()
elif state.page=="settings":
    make_settings()
else:
    make_menu()
    make_chat()

if state.needs_rerun:
    state.needs_rerun=False
    st.rerun()
    