from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="16.0.1",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="A future-proof encryption module with advanced features",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "cryptography>=3.4.7",
        "qrcode>=7.3.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
