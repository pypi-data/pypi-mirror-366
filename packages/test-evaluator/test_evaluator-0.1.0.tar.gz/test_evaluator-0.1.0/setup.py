from setuptools import setup, find_packages

setup(
    name='test-evaluator',  # must be globally unique on PyPI
    version='0.1.0',
    description='Simple library to evaluate test cases using input-output dictionaries',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/test-evaluator',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
