from setuptools import setup, find_packages

setup(
    name='suryamv-cv',
    version='0.1.0',
    author='M.V Surya',
    author_email='suryamv0507@gmail.com',
    description='A computer vision package with various image filtering and processing modules.',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)
