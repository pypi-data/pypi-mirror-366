from setuptools import setup, find_packages

setup(
    name='autovix',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn'
    ],
    author='VenkateswarluReddyLekkala',
    author_email='venkateswarlureddy647@gmail.com',
    description='Utility for automated Git cloning and app launching (React/FastAPI)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/VenkeyReddy123/autiovix.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
