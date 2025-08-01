from setuptools import setup, find_packages

setup(
    name="gitads_test_package",
    version="0.0.3",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple PyPI package to test GitAds integration.",
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/yourusername/gitads_test_package",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)
