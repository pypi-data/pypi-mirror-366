from setuptools import setup, find_packages

setup(
    name='rohan-pristine-sbert-v1',
    version='0.1.0',
    author='Rohan Kaitake',
    author_email='rohan.kaitake@pristine-code.com',
    description='Hybrid SBERT embeddings using all-MiniLM-L6-v2 and all-mpnet-base-v2.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'sentence-transformers>=2.2.0',
        'numpy>=1.20.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7',
)
