from setuptools import setup, find_packages
setup(
    name="ideal6",
    version="1.0.3",
    description="Multi-layer AES encryption library with HMAC integrity verification",
    long_description="Ideal Encryption is a secure, multi-layer encryption library that uses AES-CBC with HMAC-SHA256 to provide confidentiality and integrity for sensitive data.",
    author="AlJoharah",
    author_email="cs.alqahtani@gmail.com",
    packages=find_packages(include=["bitcrypt", "bitcrypt.", "tests", "tests."]),
    install_requires=[
        "pycryptodome"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers"
    ],
    python_requires=">=3.6",
)