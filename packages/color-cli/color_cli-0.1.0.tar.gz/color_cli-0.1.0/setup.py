from setuptools import setup, find_packages

long_description = []
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='color_cli',
    version='0.1.0',
    description='A simple coloring util for better output visibility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Abdulrahman Khaled',
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=['termcolor'],
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    python_requires='>3.10'
)