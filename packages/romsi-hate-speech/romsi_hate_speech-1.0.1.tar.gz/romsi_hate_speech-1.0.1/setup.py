from setuptools import setup, find_packages

setup(
    name="romsi_hate_speech",
    version="1.0.1",
    author="Sakun Chamikara",
    description="Detect Romanized Sinhala hate speech using mBERT.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sakunchamikara/Hate_Speech_Detection_System",
    packages=find_packages(include=["romsi_hate_speech", "romsi_hate_speech.*"]),
    install_requires=[
        "transformers",
        "torch",
        "fastapi",
        "uvicorn",
        "pydantic"
    ],
    entry_points={
        "console_scripts": [
            "romsi-detect=romsi_hate_speech.cli:main"
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
