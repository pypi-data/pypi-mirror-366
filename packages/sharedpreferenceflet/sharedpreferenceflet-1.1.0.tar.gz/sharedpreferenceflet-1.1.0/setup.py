from setuptools import setup, find_packages

setup(
    name='sharedpreferenceflet',
    version='1.1.0',
    description='Encrypted JSON-like Shared Preferences for Python',
    author='Amir Louktila',
    author_email='amir.louktila@gmail.com',
    url='https://github.com/AmirLouktaila/SharedPreferenceFlet', 
    packages=find_packages(),
    install_requires=[
        'cryptography>=3.4.7'
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
