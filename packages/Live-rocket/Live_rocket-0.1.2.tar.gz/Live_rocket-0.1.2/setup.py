from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Live_rocket',
    version='0.1.2',
    description='A dynamic, ORM-friendly HTTP framework built on Python sockets',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Bhaumik Medhekar',
    author_email='bhaumikmedhekar24@gmail.com',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # if you use MIT
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",  # or other relevant classifiers
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    project_urls={
        "Source": "https://github.com/Bhaumik0/Live-rocket",  # update accordingly
        "Documentation": "https://yourdocsurl.com"  # optional
    },
)
