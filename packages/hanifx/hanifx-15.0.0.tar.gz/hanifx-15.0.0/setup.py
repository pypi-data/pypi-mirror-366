from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="15.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "phonenumbers",
        "requests",
        "beautifulsoup4",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "hanifx=hanifx.cli:main",
        ],
    },
    python_requires=">=3.6",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="OSINT phone number info tool without APIs and permission",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
