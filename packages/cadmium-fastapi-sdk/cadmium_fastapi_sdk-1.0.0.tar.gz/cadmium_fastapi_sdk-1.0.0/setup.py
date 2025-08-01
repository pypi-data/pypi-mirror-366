from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cadmium-fastapi-sdk',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.68.0',
        'httpx>=0.24.0',
        'starlette>=0.14.0',
    ],
    description='Cadmium SDK for capturing and sending FastAPI errors.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='bannawandoor',
    author_email='connect@hasanulbanna.in',
    url='https://github.com/softwares-compound/cadmium-fastapi-sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: FastAPI',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)