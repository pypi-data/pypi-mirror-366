from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="j1939parser",
    version="0.1.4",
    description="Extracts GPS positions from J1939 PGN 65267 CAN logs",
    long_description=long_description,                      
    long_description_content_type="text/markdown",         
    author="Jagjit Singh",
    author_email="jagjit.saini2019@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        # no python-can here for lightweight base install
    ],
    extras_require={
        "can": ["python-can>=4.0.0"],  # Optional for live CAN support
    },
    python_requires=">=3.12",
)
