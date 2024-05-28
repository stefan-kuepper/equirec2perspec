from setuptools import setup, find_packages

setup(
    name='equirec2perspec',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',  # Add other dependencies here
        'opencv-python',
    ],
    author='Stefan Kuepper',
    author_email='your.email@example.com',
    description='A library to project equirectangular panorama into perspective images',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/stefan-kuepper/equirec2perspec',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
