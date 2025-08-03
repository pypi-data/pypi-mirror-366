from setuptools import setup, find_packages

setup(
    name="j1939parser",
    version="0.1.1",
    description="Extracts GPS positions from J1939 PGN 65267 CAN logs",
    author="Jagjit Singh",
    author_email="jagjit.saini2019@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        # No python-can here, so base install is lightweight
    ],
    extras_require={
        "can": ["python-can>=4.0.0"],  # Optional extra for live CAN support
    },
    python_requires=">=3.12",
)
