from setuptools import setup, find_packages

setup(
    name="Qwael",
    version="0.0.2",
    description="Easy Coding",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Bedirhan",
    author_email="bedirhan.oytpass@gmail.com",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'google-auth',
    'google-api-python-client',
    'google-auth-httplib2',
    'google-auth-oauthlib',
    'Pillow',
],
    keywords=["Google", "coding","Easy"],
    project_urls={},
    license="Proprietary",
    license_files=("LICENSE",)
)