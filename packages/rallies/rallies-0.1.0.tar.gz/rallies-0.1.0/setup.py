from setuptools import setup, find_packages
setup(
    name="rallies",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "rich",
        "requests",
        "inquirer",
        "tiktoken",
        "openai",
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'rallies=rallies.cli:main',
        ],
    },
    python_requires=">=3.6",
)