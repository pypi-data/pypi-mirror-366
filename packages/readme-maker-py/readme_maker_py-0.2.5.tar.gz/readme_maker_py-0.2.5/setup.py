from setuptools import setup, find_packages

setup(
    name="readme-maker-py",  # Replace with your package name
    version="0.2.5",  # Initial version
    author="antrishh",
    author_email="antrikshg007@gmail.com",
    description="Github readme file maker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Antriksh006/readme-file-maker",  # Your GitHub repo
    packages=find_packages(),  # Automatically discover package modules
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "groq",         # For working with Groq API
        "PyGithub",     # For interacting with GitHub
        "nbformat",     # For handling Jupyter Notebooks
        "nbconvert"     # For converting Jupyter Notebooks to Python scripts
    ],
    entry_points={
        "console_scripts": [
            "readme-maker-py=readmemaker.my_module:main",
        ],
    },
)
