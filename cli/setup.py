import setuptools


setuptools.setup(
    name="quicksplit", # Replace with your own username
    version="0.0.1",
    author="Quick Split",
    author_email="tom@quicksplit.io",
    description="The developer tool for fast, easy A/B tests",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'split = cli:base'
        ]
    },
    install_requires=[
        'click==7.0'
    ]
)
