from setuptools import setup, find_packages

setup(
    name='sqli-vuln-scanner',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'colorama',
        'fpdf'
    ],
    entry_points={
        'console_scripts': [
            'vulnscan=vulnscanner.main:main',
        ],
    },
    author='Rupesh Jha',
    description='An advanced SQLi, XSS, and Form vulnerability scanner',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
