from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='keypractice',
    version='0.1.11',
    description='A slim, cross-platform terminal-based typing trainer with YAML-based exercises and analytics.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Stephen',
    packages=find_packages(),
    install_requires=[
        'PyYAML>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'keypractice=keypractice.__main__:main',
        ],
    },
    include_package_data=True,
    package_data={
        'keypractice': ['data/*.json', 'exercises/*.yaml'],
    },
    python_requires='>=3.7',
) 