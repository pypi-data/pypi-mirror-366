from setuptools import setup, find_packages

setup(
    name='Live_rocket',
    version='0.1',
    description='A simple HTTP server framework',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        # These are only standard libraries, so not listed here.
        # No external dependencies required based on your imports.
    ],
    python_requires='>=3.6',
)
