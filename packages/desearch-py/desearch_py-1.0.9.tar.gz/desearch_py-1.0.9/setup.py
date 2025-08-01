from setuptools import setup, find_packages

setup(
    name="desearch_py",
    version="1.0.9",
    description="A Python SDK for interacting with the Desearch API service.",
    author="Desearch",
    author_email="",
    license="MIT",
    package_data={"desearch_py": ["py.typed"]},
    packages=find_packages(),
    install_requires=["openai", "requests", "typing-extensions", "pydantic"],
    python_requires=">=3.6",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
