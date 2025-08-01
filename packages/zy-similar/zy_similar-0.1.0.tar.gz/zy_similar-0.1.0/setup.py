from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zy_similar",
    version="0.1.0",
    author="Your Name",
    author_email="924179146@qq.com",
    description="A Python package for similarity analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhangzhanghua?tab=repositories",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['templates/*', 'static/*', 'public/*']
    },
    install_requires=[
        'flask>=2.0.0',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'zy_similar=__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
