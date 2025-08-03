from setuptools import setup, find_packages

setup(
    name="d1-connector",
    version="0.1.0",
    description="MySQL-style connector for Cloudflare D1 using WebSocket",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sitaram Gurjar",
    author_email="sitaramkoli987@gmail.com",
    url="https://github.com/geetflow/d1-client",
    packages=find_packages(),
    install_requires=["websockets>=11.0.3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)