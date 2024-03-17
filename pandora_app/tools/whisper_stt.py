import os
_root_=os.path.dirname(os.path.abspath(__file__))
import sys
if not sys.path[0]==_root_:
    sys.path.insert(0,_root_)
def root_join(*args):
    return os.path.join(_root_,*args)

from streamlit_mic_recorder import mic_recorder
import streamlit as st
import io
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(_root_)

def whisper_stt(openai_api_key=None,start_prompt="Start recording",stop_prompt="Stop recording",just_once=False,use_container_width=False,language=None,callback=None,args=(),kwargs={},key=None):
    if not 'openai_client' in st.session_state:
        if openai_api_key or os.getenv('OPENAI_API_KEY'):
            st.session_state.openai_client=OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        else:
            st.session_state.openai_client=None
    if not '_last_speech_to_text_transcript_id' in st.session_state:
        st.session_state._last_speech_to_text_transcript_id=0
    if not '_last_speech_to_text_transcript' in st.session_state:
        st.session_state._last_speech_to_text_transcript=None
    if key and not key+'_output' in st.session_state:
        st.session_state[key+'_output']=None
    audio = mic_recorder(start_prompt=start_prompt,stop_prompt=stop_prompt,just_once=just_once,use_container_width=use_container_width,format="webm",key=key)
    new_output=False
    if audio is None:
        output=None
    elif st.session_state.openai_client:
        id=audio['id']
        new_output=(id>st.session_state._last_speech_to_text_transcript_id)
        if new_output:
            output=None
            st.session_state._last_speech_to_text_transcript_id=id
            audio_BIO = io.BytesIO(audio['bytes'])
            audio_BIO.name='audio.webm'
            success=False
            err=0
            while not success and err<3: #Retry up to 3 times in case of OpenAI server error.
                try:
                    transcript = st.session_state.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_BIO,
                        language=language
                    )
                except Exception as e:
                    print(str(e)) # log the exception in the terminal
                    err+=1
                else:
                    success=True
                    output=transcript.text
                    st.session_state._last_speech_to_text_transcript=output
        elif not just_once:
            output=st.session_state._last_speech_to_text_transcript
        else:
            output=None
    else:
        output=None

    if key:
        st.session_state[key+'_output']=output
    if new_output and callback:
        callback(*args,**kwargs)
    return output
