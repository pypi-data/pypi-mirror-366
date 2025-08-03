from setuptools import setup, find_packages

long_description = []
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='color_cli',
    version='0.1.2',
    description='A simple coloring util for better output visibility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Abdulrahman-K-S/Color-CLI',
    author='Abdulrahman Khaled',
    author_email='AK-Salah@outlook.com',
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=['termcolor'],
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    python_requires='>3.10'
)