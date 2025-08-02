from setuptools import setup, find_packages

setup(
    name="scanpy_jupyter_roi",
    version="0.1.2",
    description="An interactive tool for drawing and filtering regions of interest on AnnData/ScanPy spatial data.",
    author="Adam Catto",
    author_email="agocatto@gmail.com",
    url="https://github.com/adamcatto/scanpy_jupyter_roi",
    packages=find_packages(),
    install_requires=[
        "scanpy==1.10.3",
        "matplotlib==3.9.2",
        "ipywidgets==8.1.5",
        "ipympl==0.9.4",
        "ipykernel==6.29.5",
        "ipython==8.29.0",
        "pandas==2.2.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
