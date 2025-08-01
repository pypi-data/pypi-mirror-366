from setuptools import setup, find_packages

setup(
    name="edf-reader",
    version="0.1.1",
    install_requires=['numpy'],
    extras_require={
        'dev': ['pytest'],
    },
    author="Vojtech Travnicek",
    author_email="vojtech.travnicek@fnusa.cz; vojtech.travnicek@wavesurfers.science",
    description="Lightweight EDF file reader, which can handle discontinuities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/bbeer_group/development/epycom/edf_reader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires='>=3.12',
    keywords='edf, edf+, edf+d, european data format, eeg, medical, neuroscience',
)
