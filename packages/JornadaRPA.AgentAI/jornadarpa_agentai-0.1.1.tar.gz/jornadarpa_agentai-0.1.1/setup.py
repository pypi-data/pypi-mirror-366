from setuptools import setup, find_namespace_packages

setup(
    name="JornadaRPA.AgentAI",
    version="0.1.1",
    author="Alex Diogo",  
    author_email="alexdiogo@desafiosrpa.com.br",
    description="Simple and powerful AI Agent with memory and tools.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["JornadaRPA.*"]),
    install_requires=[
        "openai",
        "google-generativeai",
        "requests"
    ],
    python_requires=">=3.8",
)