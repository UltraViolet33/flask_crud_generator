from setuptools import setup, find_packages

setup(
    name="flask_crud_generator",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        'Flask-SQLAlchemy',
    ],
    author="Ultraviolet33",
    description="A Flask extension to generate CRUD routes based on models.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/UltraViolet33/flask_crud_generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
