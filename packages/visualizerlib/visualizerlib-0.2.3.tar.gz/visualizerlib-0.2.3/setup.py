from setuptools import setup, find_packages
from pathlib import Path


def read_requirements():
    with open("/home/vishnu/Data2/visualizerlib/visualizerlib/requirements.txt") as f:
        return f.read().splitlines()


description = """
A simple visualization and EDA helper package. Includes:
- Agent execution for plot insights
- ML helper classes and functions
- Preprocessor, imputer, column transformer, and chaining pipeline
"""

setup(
    name="visualizerlib",
    version="0.2.3",
    packages=find_packages(),
    install_requires=[
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "groq",
    "langchain",
    "pydantic",
    "langchain-core",
    "ipython",
    "scikit-learn",
    "tqdm",
    ],
    author="Vishnu",
    author_email="vishnurrajeev@gmail.com",
    description=description,  # Keep this short
    long_description=Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/Vishnuu011/visualizerlib",  # Remove /tree/main for PyPI compatibility
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)


