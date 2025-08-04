from setuptools import setup, find_packages

setup(
    name="cf-auto-bypass",  # Yeni benzersiz isim
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.54.0",
    ],
    author="AreYouDev",
    author_email="your.email@example.com",
    description="A Python library to automatically bypass Cloudflare protection",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cf-auto-bypass",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)