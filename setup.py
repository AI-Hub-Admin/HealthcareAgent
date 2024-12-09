# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'requests>=2.17.0',
    'beautifulsoup4>=4.10.0',
    'cachetools>=4.0.0',
    'numpy>=1.20.0',
    'func-timeout>=4.3.0'
]

extras = dict()
extras['dev'] = ['flask>=2.0.0']
extras['test'] = extras['dev'] + []

setup(
    name="HealthcareAgent",  # Required
    version="0.0.2",    # Required
    description="Open API of Public Website to get AI Agents in Healthcare Applications",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email="aihubadmin@126.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="API,Healthcare,AI Agent",
    packages=find_packages(where="src"),  # Required
    package_data={'HealthcareAgent.data': ['*.txt']},    
    package_dir={'': 'src'},
    python_requires=">=3.4",
    project_urls={
        "homepage": "http://www.deepnlp.org/search/agent/",
        "repository": "https://github.com/AI-Hub-Admin/HealthcareAgent"
    },
)
