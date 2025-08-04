from setuptools import setup, find_packages

setup(
    name="cua-sdk",
    version="0.1.0",
    description="A reusable Python SDK for controlling a computer-using agent in a virtual desktop.",
    author="Elias Tsoukatos",
    author_email="your.email@example.com",
    url="https://github.com/eliastsoukatos/computer_use",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
