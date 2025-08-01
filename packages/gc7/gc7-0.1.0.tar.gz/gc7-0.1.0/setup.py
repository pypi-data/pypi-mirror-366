from setuptools import setup, find_packages

setup(
    name="gc7",  # nom sur PyPI
    version="0.1.0",
    author="GrCOTE7",
    description="Un module avec plein d'outils utiles pour dev en PyMoX",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],  # ajoute ici tes dépendances éventuelles
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
