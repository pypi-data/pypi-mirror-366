from setuptools import setup, find_packages

setup(
    name='megarnucleusx',
    version='0.0.2.6',
    author='luis',
    author_email='gachaprimosxd128@gmail.com',
    description='Un micro-framework de IA que utiliza micronumpy para el cálculo numérico.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TuUsuario/megarnucleusx',
    packages=find_packages(),
    # ¡NUEVA SECCIÓN DE DEPENDENCIAS!
    install_requires=[
        'micronumpy>=0.1.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.6',
)
