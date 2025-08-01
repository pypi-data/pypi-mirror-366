from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='request_response_logging',
    version='1.0.5',
    author='Pravin Tiwari',
    author_email='pravint198@gmail.com',
    description='Django logger to log request response',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['simplejson'],
    python_requires='>=3.7'
)
