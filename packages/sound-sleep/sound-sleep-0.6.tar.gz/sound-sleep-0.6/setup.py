from setuptools import setup, find_packages

setup(
    name="sound-sleep",
    version="0.6",
    description="SoundSleep is a Python package for extracting comprehensive sleep features from wearable or sleep stage-labeled data.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Trym Drag-Erlandsen, Alireza Delfarah, and Chuyi Zhang",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy"
    ],
    python_requires=">=3.7",
)
