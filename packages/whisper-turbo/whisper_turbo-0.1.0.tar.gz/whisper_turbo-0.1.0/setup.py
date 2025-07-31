"""
Setup script for MLX Whisper Transcriber
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whisper-turbo",
    version="0.1.0",
    author="Nathan Metzger",
    author_email="nathan.metzger@voxtria.com",
    description="High-performance Whisper transcription with Turbo v3 for Apple Silicon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xbattlax/whisper-turbo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mlx-whisper>=0.1.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "whisper-turbo=whisper_turbo.cli:main",
        ],
    },
    keywords="whisper, turbo, transcription, speech-to-text, mlx, apple-silicon, metal, audio, whisper-turbo",
    project_urls={
        "Bug Reports": "https://github.com/xbattlax/whisper-turbo/issues",
        "Source": "https://github.com/xbattlax/whisper-turbo",
        "Documentation": "https://github.com/xbattlax/whisper-turbo#readme",
    },
)