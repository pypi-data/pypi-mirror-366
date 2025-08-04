from setuptools import setup, find_packages
import makeitaquote

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="makeitaquote",
    version= makeitaquote.__version__,
    author="Ryo001339",
    description="DiscordBOT用のmake it a quote生成パッケージです",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/veda00133912/makeitaquote",
    project_urls={
        "Bug Tracker": "https://github.com/veda00133912/makeitaquote/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="discord, makeitaquote, image, generator, bot",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)