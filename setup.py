from setuptools import setup, find_packages

setup(
    name="flask_crud_generator",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
    ],
    author="Ultraviolet33",
    description="A Flask extension to generate CRUD routes based on models.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
