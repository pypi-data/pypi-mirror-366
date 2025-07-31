from setuptools import setup, find_packages

setup(
    name='gensarpy',
    version='0.1.2',
    author='Gencer',
    author_email='gencersarpmert3@gmail.com',
    description='A Python library for testing the convergence of mathematical series.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/gensarpy',  # Replace with your GitHub URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'sympy',
    ],
)
