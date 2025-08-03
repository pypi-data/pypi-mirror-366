from setuptools import setup, find_packages

setup(
    name = 'nofex-hack',
    version = "0.0.1",
    description = "This is a Python library for hacking and security.",
    author="kasra kiani",
    author_email="kasrakini011@gmail.com",
    packages=find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    readme = "README.md",
    dependencies = [
    "phonenumbers",
    "pyautogui",
    "requests",
    "beautifulsoup4",
    "psutil",
    "rotate-screen",
    "pynput",
    ],




)