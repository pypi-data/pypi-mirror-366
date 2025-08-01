from setuptools import setup, find_packages

setup(
    name="nt_pygrambot",
    version="0.1.0",
    author="SN01",
    description="Python Telegram Bot",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ziyocamp/py-gram-bot/pygrambot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
