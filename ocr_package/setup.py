from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ocr",
    version="0.1.0",
    description="A Python package for extracting text from scanned PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Original Author",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pytesseract>=0.3.0",
        "pdf2image>=1.16.0",
        "Pillow>=9.0.0",
        "opencv-python>=4.5.0",
        "PyMuPDF>=1.19.0",
        "numpy>=1.19.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "advanced": [
            "transformers>=4.0.0",
            "torch>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ocr=ocr_cli:main",
            "ocr-advanced=advanced_cli:main",
            "ocr-batch=batch_cli:main",
        ],
    },
) 