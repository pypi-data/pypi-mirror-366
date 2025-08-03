from setuptools import setup, find_packages

setup(
    name="textcleaner-partha",
    version="1.1.2",
    description="Reusable text preprocessing library for NLP tasks",
    author="Dr. Partha Majumdar",
    author_email="partha.majumdar@hotmail.com",
    url="https://github.com/partha6369/textcleaner",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "spacy>=3.0.0",
        "autocorrect==0.4.4",
        "contractions>=0.1.73",
        "beautifulsoup4>=4.12.0",
        "python-docx>=0.8.11",
        "pypdf>=3.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)