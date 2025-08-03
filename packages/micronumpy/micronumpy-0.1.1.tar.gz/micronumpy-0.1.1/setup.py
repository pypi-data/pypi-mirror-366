from setuptools import setup, find_packages
import pathlib

# Lee el README.md para la descripción larga
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='micronumpy',
    version='0.1.1',  # Actualiza la versión
    author='TuNombre',
    author_email='tu@email.com',
    description='Una implementación ligera y pura en Python de la API esencial de NumPy con autograd básico.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/micronumpy',  # Cambia por la URL real de tu repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.6',
    install_requires=[
        # Aquí puedes poner dependencias externas si las tienes, por ahora está vacía porque es puro Python
    ],
    keywords='numpy autograd deep learning neural networks scientific computing',
    project_urls={  # URLs adicionales que aparecen en PyPI
        "Bug Tracker": "https://github.com/TuUsuario/micronumpy/issues",
        "Source": "https://github.com/TuUsuario/micronumpy",
        "Documentation": "https://github.com/TuUsuario/micronumpy#readme",
        "Changelog": "https://github.com/TuUsuario/micronumpy/releases",
    },
)
