from setuptools import setup
from pathlib import Path

setup(
    name="bday-song",
    version="1.0.0",
    description="Happy Birthday beep CLI tool for Linux",
    author="Turtledevv",
    packages=["birthday"],
    entry_points={
        'console_scripts': [
            'birthday = birthday.__main__:main',
        ],
    },
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
	"Topic :: Multimedia :: Sound/Audio",
	"License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6'
)
