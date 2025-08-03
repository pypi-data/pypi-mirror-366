from setuptools import setup, find_packages

# Open README.md and read its contents
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="test-evaluator",  # must be globally unique on PyPI
    version="0.1.2.dev1",
    author="Devashish Varanasi",
    author_email="varanasidevashish@gmail.com",
    description="Evaluate test cases using input/output dictionaries",
    long_description=long_description,  # ← this is critical
    long_description_content_type="text/markdown",  # ← tells PyPI to render markdown
    url="https://github.com/Devashish-Varanasi/test-evaluator",  # update with your repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)