from setuptools import setup, find_packages

setup(
    name="verahession",
    version="0.1.4",
    author="Jack Hession",
    author_email="jack@hessiondynamics.com",
    description="Python client library for Vera AI chatbot by Hession Dynamics",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hession-dynamics/hd-vera-lib",
    packages=find_packages(where=".", exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    license="MIT",
)
