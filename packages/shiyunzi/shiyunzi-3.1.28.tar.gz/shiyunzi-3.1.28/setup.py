from setuptools import setup, find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('shiyunzi')

setup(
    name="shiyunzi",
    version="3.1.28", 
    packages=find_packages(),
    package_data={
        'shiyunzi': extra_files,
    },
    include_package_data=True,
    install_requires=[
        "Pillow>=9.5.0",
        "PyQt6>=6.4.0",
        "setuptools>=65.5.1",
        "wheel>=0.38.4",
        "runwayapi>=0.2.1",
        "PJYSDK>=1.0.8",
        "peewee>=3.16.2",
        "openai>=1.3.7",
        "moviepy==1.0.0",  # 修改为包含editor子模块
        "cakegeminiapi>=0.1.8",
        "webuiapi>=0.0.1",
        "ffmpeg-python>=0.2.0",
        "requests-aws4auth>=1.2.0",
        "aiohttp>=3.9.0",
        "httpx>=0.25.0",
        "fastapi>=0.104.0",
        "playwright>=1.40.0",
        "pydantic>=2.5.0",
        "ffmpeg-binaries-compat>=1.0.1"
    ],
    entry_points={
        'console_scripts': [
            'shiyunzi=shiyunzi.main:main',
        ],
    }
)