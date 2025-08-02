from setuptools import setup, find_packages

setup(
    name="xyzzy3",
    version="0.1.0",
    description="Reserved package name to prevent dependency confusion attacks.",
    long_description="This package exists only to reserve the name 'xyzzy3'.",
    long_description_content_type="text/plain",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    python_requires=">=3.6",
)
