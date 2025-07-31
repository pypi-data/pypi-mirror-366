
from setuptools import setup, find_packages

setup(
    name="tsengmodtool",
    version="3.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'tsengmodtool = tsengmodtool.__main__'
        ]
    },
    author="林安潔 (tseng1010)",
    author_email="tseng1010@users.noreply.pypi.org",
    description="中文化的《貓咪大戰爭》存檔修改工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
