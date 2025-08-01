from setuptools import setup, find_packages

setup(
    name='overinstall',
    version='0.1.0',
    description='Auto-installs all Python dependencies for your project',
    author='xxDawid',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
