from setuptools import setup, find_packages

setup(
    name="synapso",
    version="0.3.2",
    description="Meta-package that installs synapso-core and synapso-cli.",
    author="Ganesh Palanikumar",
    author_email="me@ganeshpalanikumar.dev",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "synapso-core==0.1.5",
        "synapso-cli==0.2.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)
