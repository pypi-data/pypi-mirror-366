from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="diff-reviewer",
    version="0.1.1",
    description="AI-based local code diff reviewer that runs on every git commit.",
    author="Vatsalya Bajpai",
    author_email="vatsalyabajpai03@example.com",
    url="https://github.com/ChargedMonk/DiffReviewer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["llama-cpp-python==0.3.8", "gdown==5.2.0"],
    entry_points={
        "console_scripts": [
            "diff-reviewer=diff_reviewer.main:main"
        ]
    },
    package_data={
        "": ["../hooks/pre-commit"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
