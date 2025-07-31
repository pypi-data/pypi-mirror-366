from setuptools import setup, find_packages

setup(
    name="jiso-droid",
    version="1.1.0-dev2",
    packages=find_packages(include=['jiso_droid*']),
    description="JISO-DROID - Keystore Generator & APK Signing Tool",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Jhosua",
    author_email="echobytehax@gmail.com",
    entry_points={
        'console_scripts': [
            'jiso=jiso_droid.jiso:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)