
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pandora_app",
    version="0.0.48",
    author="Baptiste Ferrand",
    author_email="bferrand.maths@gmail.com",
    description="Streamlit interface for the pandora_ai project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B4PT0R/pandora_app",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pandora = pandora_app.launch_app:main',
        ],
    },
    package_data={
        'pandora_app': [
            'launch_app.py',
            '.streamlit/*',
            'app_images/*',
            'app_config.json',
            "quick_help.md"
        ],
    },
    install_requires=[
        "pandora-ai",
        "streamlit-stacker",
        "firebase-user",
        'google-api-python-client',
        'gTTS',
        'objdict-bf',
        'python-dotenv',
        'seleniumbase',
        'spotipy',
        'streamlit',
        'streamlit-code-editor',
        'streamlit-input-box',
        'streamlit-mic-recorder',
        'streamlit-TTS',
        'matplotlib',
        'numpy',
        'seaborn',
        'pandas',
        'graphviz',
        'altair',
        'plotly',
        'bokeh',
        'pydeck',
        'scipy',
        'sympy',
        'scikit-learn',
        'vega-datasets'
    ],
)
