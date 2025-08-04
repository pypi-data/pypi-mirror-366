from setuptools import setup,find_packages

setup(
    name="abu_color",
    version="0.1",
    author="Abujelal Man",
    description="Terminal color formatter with foreground, background, and style support",
    long_description=open("READMD.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
      ],
)
