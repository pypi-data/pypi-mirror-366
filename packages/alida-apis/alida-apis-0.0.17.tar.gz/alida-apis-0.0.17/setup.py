import setuptools

setuptools.setup(
    name="alida-apis",
    version="0.0.17",
    author="Alida research team",
    author_email="salvatore.cipolla@eng.it",
    description="Python APIs for interaction with ALIDA backend.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires = [
        "requests",
        "boto3",
        "minio",
        "progressbar",
        "pandas"
        ],
)
