from setuptools import setup, find_packages

setup(
    name='ediversity',
    version='0.1.0',
    description='A minimal toolkit for molecular diversity using Vendi and Hamiltonian scores.',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'scikit-learn',
        'rdkit',
    ],
    entry_points={
        'console_scripts': [
            'ediversity = ediversity.eDiversity:main',
            'vendi_score = ediversity.vendi_score:main',
            'hamiltonian_score = ediversity.hamiltonian_score:main',
        ],
    },
    python_requires='>=3.7',
)
