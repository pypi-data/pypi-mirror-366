from setuptools import setup, find_packages

setup(
    name="lnkdnlng",
    version="1.0.0",
    description="A cli interpreter for LinkedInLanguage.",
    author="whirlxd",
    author_email="lnkdnlng@whirlxd.dev",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lnkdnlng=lnkdnlng.main:main",  
        ],
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
