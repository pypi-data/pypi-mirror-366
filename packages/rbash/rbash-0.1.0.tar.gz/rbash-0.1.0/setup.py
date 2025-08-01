from setuptools import setup, find_packages

setup(
    name="rbash",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'rbash = rbash.cli:main',
        ],
    },
    package_data={
        'rbash': ['rbash.sh'],
    },
    author="Your Name",
    description="Remote bash shell with local SSHFS mounting using reverse tunnel.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",
)