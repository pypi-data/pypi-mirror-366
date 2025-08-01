from setuptools import setup, find_packages

setup(
    name="anujscanpro",
    version="0.1.0",
    author="Anuj Prajapati",
    author_email="your-email@example.com",
    description="AnujScan Pro - A modular recon & vulnerability analysis toolkit",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/anujscan",  # optional
    packages=find_packages(),
    install_requires=[
        "pyfiglet",
        "colorama",
        "yaspin",
        "requests",
        "dnspython"
    ],
    entry_points={
        "console_scripts": [
            "anujscan=anujscan.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
