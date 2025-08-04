from setuptools import setup, find_packages

setup(
    name="SGLab-tools",
    version="1.0.3",
    author="Etienne Ntumba Kabongo",
    author_email="etienne.ntumba.kabongo@umontreal.ca",  # mets ton courriel
    description="Outils CLI pour l’analyse comparative de génomes bactériens",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/EtienneNtumba/SGLab-tools",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "sglab=sglabtools.cli:app",  # ← CLI basée sur typer
        ],
    },
    install_requires=[
        "typer>=0.9",
        "pandas",
        "biopython",
        "matplotlib",
        "seaborn",
        "openpyxl"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)
