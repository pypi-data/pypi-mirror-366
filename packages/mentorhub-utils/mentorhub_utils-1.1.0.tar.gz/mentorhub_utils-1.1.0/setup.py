from setuptools import setup, find_packages

# Safely read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mentorhub-utils',
    version='1.1.0',
    description='Helper utilities for Mentorhub API projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Agile Learning Institute',
    author_email='devs@agile-learning.institute',
    url='https://github.com/agile-learning-institute/mentorHub-utils',
    packages=find_packages(),
    install_requires=[
        "flask",
        "pymongo",
        "joserfc"
    ],
    license='Apache-2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)