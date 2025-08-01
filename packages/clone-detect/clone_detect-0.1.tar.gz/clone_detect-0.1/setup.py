# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='clone-detect',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'clone-detect=clone_detect.cli:main'
        ],
    },
    install_requires=[],
    author='Naila',
    description='Find duplicate files by content hash',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='duplicate files, hash, dedupe, cleaner',
    url='https://github.com/yourusername/clone-detect',  # <-- update with your repo URL
    license='MIT',  # <-- update if you use a different license
    python_requires='>=3.7',
)
