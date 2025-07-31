from setuptools import setup, find_packages
import os
import re

def get_version():
    with open(os.path.join("kaygraph", "__init__.py"), "r") as f:
        return re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="kaygraph",
    version=get_version(),
    packages=find_packages(),
    author="KayOS Team",
    author_email="team@kayos.ai",
    description="A context-graph framework for building production-ready AI applications.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/KayOS-AI/KayGraph",
)
