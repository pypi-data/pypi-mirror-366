from setuptools import setup, find_packages

setup(
    name='smpldta',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        "reportlab"
    ],
    entry_points={
        'console_scripts': [
            'smpldta=smpldta.cli:main',
        ],
    },
    description='Fetch unique sample data like images, videos, code, GIFs, text, and JSON files.',
    author='Parteek',
    author_email='prateekahlawat1223@gmail.com',
    url='https://github.com/parteekahlawat/smpldta',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
)