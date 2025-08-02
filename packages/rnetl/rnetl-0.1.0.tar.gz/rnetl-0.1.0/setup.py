import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rnetl",
    license="MIT License",
    author="Huaiwei Sun",
    author_email="hsun@hust.edu.cn",
    description="A Python package for network logic operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HuaiweiSun/rnetl",
    download_url="https://github.com/HuaiweiSun/rnetl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent"
    ],
)
