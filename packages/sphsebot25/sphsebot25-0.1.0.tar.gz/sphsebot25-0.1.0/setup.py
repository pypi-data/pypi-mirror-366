from setuptools import setup, find_packages

setup(
    name='sphsebot25',
    version='0.1.0',
    description='A smart AI-based games and logic package including maze solving, Connect4, TicTacToe, and pattern prediction.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'seaborn',
        'python-chess',
        'chess'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
