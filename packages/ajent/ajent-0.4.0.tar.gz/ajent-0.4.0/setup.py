from setuptools import setup, find_packages

setup(
    name='ajent',
    version='0.4.0',
    packages=find_packages(),
    install_requires=[
        'openai'
    ],
    author="Gustavo Barros",
    author_email="gbarrospe@gmail.com",
    description="Library to implement your own Ajent Server API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)