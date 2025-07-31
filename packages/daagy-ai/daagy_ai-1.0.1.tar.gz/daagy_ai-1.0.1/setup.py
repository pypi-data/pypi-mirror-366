from setuptools import setup, find_packages

setup(
    name="daagy-ai",  
    version="1.0.1",
    author="Vibhor Jaiswal",
    author_email="vibhor.jaiswal9.9@gmail.com",
    description="Daagy is a terminal-based AI assistant that follows natural language instructions to perform system tasks, answer questions, and much more.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VibhorJaiswal/daagy-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "google-genai"
    ],
    entry_points={
        "console_scripts": [
            "daagy = daagy.__init__:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
