from setuptools import setup, find_packages

setup(
    name='sminitorch',
    version='0.1.0',
    author='TuNombre',
    author_email='tu@email.com',
    description='Un framework de deep learning minimalista, con tensores y autograd, que utiliza micronumpy como backend.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/sminitorch',
    packages=find_packages(),
    install_requires=[
        'micronumpy>=0.1.2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.6',
)
