#!/usr/bin/env python3
"""
Setup script for TCP Port and Ping Checker
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="tcp-port-checker",
    version="1.0.2",
    author="iturkyilmazoglu",
    author_email="ismail.turkyilmazoglu@gmail.com",
    description="A powerful network connectivity analyzer with real-time system monitoring and IPv6 support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ismailTrk/tcp-port-checker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "tcp-port-checker=main:main",
            "netcheck=main:main",
        ],
    },
    keywords="network, tcp, port, checker, ping, monitoring, connectivity, scanner",
    project_urls={
        "Bug Reports": "https://github.com/ismailTrk/tcp-port-checker/issues",
        "Source": "https://github.com/ismailTrk/tcp-port-checker",
        "Documentation": "https://github.com/ismailTrk/tcp-port-checker#readme",
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
)
