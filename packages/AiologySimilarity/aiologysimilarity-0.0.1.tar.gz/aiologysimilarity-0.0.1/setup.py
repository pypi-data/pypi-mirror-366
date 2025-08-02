from setuptools import setup , find_packages

with open("README.md","r") as file:
    readme = file.read()

setup(
    name="AiologySimilarity",
    version="0.0.1",
    author="Seyed Moied Seyedi (Single Star)",
    packages=find_packages(),
    install_requires=[
        "opencv-python","numpy","setuptools"
    ],
    license="MIT",
    description="Subset of Aiology package",
    long_description=readme,
    long_description_content_type="text/markdown"
)