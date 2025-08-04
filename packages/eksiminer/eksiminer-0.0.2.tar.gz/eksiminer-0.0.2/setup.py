from setuptools import setup, find_packages


with open("Readme.md", "r") as f:
    long_description = f.read()


setup(
    name="eksiminer",
    version="0.0.2",
    description="eksiminer is a Python package for scraping entries, topics, authors, and daily highlights from eksisozluk.com",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/okanyenigun/eksi-scrap",
    author="Okan Yenigün",
    author_email="okanyenigun@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'selenium==4.28.1',
        'beautifulsoup4==4.12.3',
        'python-slugify==8.0.4',
        'undetected-chromedriver==3.5.5',
        'webdriver-manager==4.0.2',
        'pydantic==2.11.7',
    ],
    python_requires='>=3.7',
)
