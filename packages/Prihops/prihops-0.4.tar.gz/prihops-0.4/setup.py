from setuptools import setup, find_packages

setup(
    name="Prihops",
    version="0.4",
    description="Google drive integration",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Bedirhan",
    author_email="bedirhan.oytpass@gmail.com",
    url="",
    packages=find_packages(),
    py_modules=["Prihops"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["google.oauth2","googleapiclient.discovery","googleapiclient.http","PIL","io"],
    keywords=["Google", "DRİVE","entegration"],
    project_urls={},
)