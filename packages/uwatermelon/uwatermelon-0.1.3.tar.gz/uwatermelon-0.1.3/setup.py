from setuptools import setup, find_packages

setup(
    name='uwatermelon',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[],
    author='あいうえお',
    description='日本語で書ける謎の言語「うぉーたーめろん」',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Japanese',
    ],
    python_requires='>=3.6',
)
