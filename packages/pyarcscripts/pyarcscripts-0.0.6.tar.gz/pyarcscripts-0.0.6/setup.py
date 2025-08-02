from setuptools import setup, find_packages

setup(
    name="pyarcscripts",
    version="0.0.0000006",
    author="INICODE",
    author_email="contact.inicode@gmail.com",
    description="Paquetage Python qui stocke toutes les fonctionnalités utiles de pyArc pouvant être utilisé dans tous projets et modules pyArc",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/inicode_celestin03/pyarcscripts",
    packages=find_packages(),
    install_requires=[
        "python-multipart>=0.0.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)