from setuptools import setup, find_packages

setup(
    name="webpys",
    version="4.5.0",
    author="Pugazh@TheHacker",
    author_email="youremail@example.com",
    description="A web passive scanner and recon tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Pugazh2006/Webpys",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
    ],
    entry_points={
        'console_scripts': [
            'webpys=webpys.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
