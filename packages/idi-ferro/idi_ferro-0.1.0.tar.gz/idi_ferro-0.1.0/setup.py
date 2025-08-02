from setuptools import setup, find_packages

setup(
    name="idi-ferro",
    version="0.1.0",
    description="Reserved package to prevent dependency confusion.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    python_requires=">=3.6",
)
