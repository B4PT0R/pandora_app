
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pandora_app",
    version="0.0.32",
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
    # Include the launch script in the package data
    package_data={
        'pandora_app': [
            'launch_app.py',
            '.streamlit/*',  # Include all files in the .streamlit folder
            'app_images/*',  # Include all files in the app_images folder
            'app_config.json'
        ],
    },
    # Specify the dependencies
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
