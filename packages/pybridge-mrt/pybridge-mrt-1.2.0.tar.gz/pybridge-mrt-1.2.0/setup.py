from setuptools import setup, find_packages


setup(
    name='pybridge-mrt',
    version="1.2.0",
    author="Mohammad Reaza Taghdiri",
    author_email="m40465271@gmail.com",
    description="A library for sharing data between python scripts",
    long_description= open("README.md").read(),
    long_description_content_type = 'text/markdown',
    packages=find_packages(),
    
)