from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="phylofunc",
    version='1.0.9',
    author="Luman Wang",
    author_email="wangluman@bjmu.edu.cn",
    description='Generate phylofunc to incorporate microbiome phylogeny to inform on metaproteomic functional distance.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['pandas','Bio'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={
        '': ['data/*.nwk', 'data/*.csv', '*.ipynb'],
    },
)









