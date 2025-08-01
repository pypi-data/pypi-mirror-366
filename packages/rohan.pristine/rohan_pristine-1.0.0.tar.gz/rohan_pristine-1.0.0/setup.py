from setuptools import setup, find_packages

setup(
    name="rohan.pristine",
    version="1.0.0",
    description="Pristine SBERT - Custom Resume Screening Model",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    package_data={
        "rohan_pristine": ["model_files/*"]
    },
    install_requires=[
        "sentence-transformers>=2.2.2",
        "torch>=1.12.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)