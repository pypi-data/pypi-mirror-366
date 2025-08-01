from setuptools import setup, find_packages

def get_version():
    version = {}
    with open('wp21_train/utils/version.py') as f:
        exec(f.read(), version)
    return version['__version__']

setup(
    name="wp21_train",
    version=get_version(),
    author="Ioannis Xiotidis",
    author_email="ioannis.xiotidis@cern.ch",
    description="Framework that provides tools allowing for monitoring training of ML models with the aim to be executed in firmware developed under the ATLAS NextGen WP21 project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/atlas-nextgen-wp21/trainining_framework.git",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21,<2.0",
        "PyYAML>=6.0.0,<7.0.0",],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    python_requires='>=3.6',
)
