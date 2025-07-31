from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="quoridor-env",
    version="0.1.6",
    description="Python Quoridor game engine with Gym environment for RL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Christian Contreras",
    author_email="chrisjcc@users.noreply.github.com",
    url="https://github.com/chrisjcc/quoridor",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gymnasium>=0.28.0",
        "numpy>=1.23",
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
        "uvicorn[standard]>=0.24.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
    keywords="quoridor gymnasium reinforcement-learning board-game",
    include_package_data=True,
)
