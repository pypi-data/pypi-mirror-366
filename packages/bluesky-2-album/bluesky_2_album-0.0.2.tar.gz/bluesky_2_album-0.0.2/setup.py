import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bluesky_2_album",
    version="0.0.2",
    author="Yunzhi Gao",
    author_email="gaoyunzhi@gmail.com",
    description="Return photo list and caption (markdown format) from bluesky.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gaoyunzhi/bluesky_2_album",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pyyaml',
        'telegram_util',
    ],
    python_requires='>=3.0',
)