import streamlit as st
from code_editor import code_editor

class code_editor_output_parser:
    def __init__(self):
        self.last_id=None

    def __call__(self,output):
        content=output["text"]
        if not output['id']==self.last_id:
            self.last_id=output['id']
            if not output["type"]=='':
                event=output["type"]
            else:
                event=None
        else:
            event=None
        return event,content

extension_to_language={
    '':'plaintext',
    '.txt': 'plaintext',
    '.py': 'python',
    '.js': 'javascript',
    '.java': 'java',
    '.rb': 'ruby',
    '.php': 'php',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.swift': 'swift',
    '.go': 'go',
    '.ts': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.json': 'json',
    '.xml': 'xml',
    '.sh': 'bash',
    '.md': 'markdown',
    '.sql': 'sql',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.r': 'r',
    '.kt': 'kotlin',
    '.rs': 'rust',
    '.dart': 'dart',
    '.lua': 'lua',
    '.pl': 'perl',
    '.ps1': 'powershell',
    '.bat': 'batch',
    '.h': 'c',
    '.c': 'c',
    '.f': 'fortran',
    '.jl': 'julia',
    '.tex': 'latex',
    '.lisp': 'lisp',
    '.ini': 'ini',
    '.toml': 'toml',
    '.vbs': 'vbscript',
    '.rkt': 'scheme',
    '.asm': 'assembly',
    '.vhdl': 'vhdl',
    '.verilog': 'verilog',
    '.matlab': 'matlab',
    '.groovy': 'groovy',
    '.puppet': 'puppet',
    '.erl': 'erlang',
    '.hs': 'haskell',
    '.ml': 'ocaml',
    '.scala': 'scala',
    '.elm': 'elm',
    '.clj': 'clojure',
    '.coffee': 'coffeescript',
    '.ex': 'elixir',
    '.nim': 'nim',
    '.pas': 'pascal',
    '.prg': 'clipper',
    '.sas': 'sas',
    '.st': 'smalltalk',
    '.tcl': 'tcl',
    '.vb': 'vbnet',
    '.zig': 'zig'
}

def ext_to_lang(ext):
    if ext in extension_to_language:
        return extension_to_language[ext]
    else:
        return 'plaintext'

def editor(*args,lang=None,**kwargs):

    if not 'code_editor_output_parser' in st.session_state:
        st.session_state.code_editor_output_parser=code_editor_output_parser()

    css_string = '''
    background-color: #bee1e5;

    body > #root .ace-streamlit-dark~& {
    background-color: #262830;
    }

    .ace-streamlit-dark~& span {
    color: #fff;
    opacity: 0.6;
    }

    span {
    color: #000;
    opacity: 0.5;
    }

    .code_editor-info.message {
    width: inherit;
    margin-right: 75px;
    order: 2;
    text-align: center;
    opacity: 0;
    transition: opacity 0.7s ease-out;
    }

    .code_editor-info.message.show {
    opacity: 0.6;
    }

    .ace-streamlit-dark~& .code_editor-info.message.show {
    opacity: 0.5;
    }
    '''
    # create info bar dictionary
    info_bar = {
    "name": "language info",
    "css": css_string,
    "style": {
                "order": "1",
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "center",
                "width": "100%",
                "height": "2.5rem",
                "padding": "0rem 0.75rem",
                "borderRadius": "8px 8px 0px 0px",
                "zIndex": "9993"
            },
    "info": [{
                "name": "",
                "style": {"width": "100px"}
            }]
    }

    x=lambda i:str(i)+'%'

    buttons=[
        {
            "name": "New",
            "feather": "File",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","new"]
            ],
            "style": {
            "left":x(1)
            }
        },
        {
            "name": "Open",
            "feather": "Folder",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","open"]
            ],
            "style": {
            "left":x(12)
            }
        },
        {
            "name": "Save",
            "feather": "Save",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                "submit"
            ],
            "style": {
            "left":x(24)
            }
        },
        {
            "name": "Save as",
            "feather": "Copy",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","save_as"]
            ],
            "style": {
            "left":x(36)
            }
        },
        {
            "name": "Rename",
            "feather": "Edit",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","rename"]
            ],
            "style": {
            "left":x(51)
            }
        },
        {
            "name": "Delete",
            "feather": "Trash",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","delete"]
            ],
            "style": {
            "left":x(66)
            }
        },
        {
            "name": "Run",
            "feather": "Play",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","run"]
            ],
            "style": {
            "left":x(79)
            }
        },
        {
            "name": "Close",
            "feather": "XSquare",
            "primary": True,
            "hasText": True,
            "alwaysOn": True,
            "showWithIcon": True,
            "commands": [
                ["response","close"]
            ],
            "style": {
            "left":x(89)
            }
        }
    ]
    kwargs.update(
        theme='default',
        lang=lang or 'plaintext',
        buttons=buttons,
        info=info_bar
        )

    output=code_editor(*args,**kwargs)
    return st.session_state.code_editor_output_parser(output)


