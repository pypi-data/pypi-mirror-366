from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="streamlit-keycloak-lex",
    version="1.0.5",
    author="Melih Sünbül",
    author_email="m.sunbul@lund-it.com",
    description="Keycloak authentication for Streamlit",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/LundIT/streamlit-keycloak-lex",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit-local-storage",
        "streamlit >= 0.63",
    ],
)
