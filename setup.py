from setuptools import setup, find_packages

setup(
    name="leapcell",
    keywords=["back-end", "framework", "RESTful"],
    version="0.0.8",
    description="leapcell python client",
    author="aljun",
    author_email="gagasalamer@outlook.com",
    license="Apache",
    url="https://docs.leapcell.io",
    install_requires=[
        "urllib3 >= 2.1.0",
    ],
    python_requires=">=3.5",
    packages=["leapcell"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
