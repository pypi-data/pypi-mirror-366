from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-ag-grid",
    version="0.0.1",
    description="Reserved package name for django-ag-grid.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="django-ag-grid Maintainer",
    author_email="email@example.com",
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)