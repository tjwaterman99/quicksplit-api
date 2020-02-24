import setuptools
import os


setuptools.setup(
    name="quicksplit",
    version=os.environ.get('RELEASE_VERSION') or '0.0.0',
    author="Quick Split",
    author_email="tom@quicksplit.io",
    description="The developer tool for fast, easy A/B tests",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'quicksplit = cli:base'
        ]
    },
    install_requires=[
        'click==7.0',
        'requests==2.23.0',
        'terminaltables==3.1.0'
    ]
)
