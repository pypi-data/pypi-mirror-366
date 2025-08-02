from setuptools import setup, find_packages

setup(
    name="twoprompt",
    version="1.0.7",
    description="twoprompt is a python cli that allows you to prompt different LLMs",
    packages=find_packages(where="cli"),
    
    url="https://github.com/Jamcha123/twoPrompt",
    entry_points={
        "console_scripts": [
            'prompt=twoPrompt.index:main'
        ]
    }
)