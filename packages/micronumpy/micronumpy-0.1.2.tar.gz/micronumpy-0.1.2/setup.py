from setuptools import setup, find_packages

setup(
    name='micronumpy',
    version='0.1.2',
    author='luis',
    author_email='gachaprimosxd128@gmail.com',
    description='Una implementación ligera y pura en Python de la API de NumPy para proyectos sin dependencias pesadas.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/micronumpy',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.6',
)
