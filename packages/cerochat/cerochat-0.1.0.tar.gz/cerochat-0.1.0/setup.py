from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cerochat",
    version="0.1.0",
    author="Cerodev",
    author_email="cerodevcorp@gmail.com",
    description="Real-time chat application | Made my Cerodev.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "supabase>=2.0.0",
        "requests>=2.28.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "cerochat=cerochat.main:main",
        ],
    },
)