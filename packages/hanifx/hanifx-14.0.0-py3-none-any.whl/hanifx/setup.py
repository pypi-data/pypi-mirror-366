from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="13.0.0",
    author="Hanif",
    description="PyPI uploader without twine using requests",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "hanifx-upload=hanifx.uploader.cli:main"
        ]
    },
    python_requires=">=3.6",
)
