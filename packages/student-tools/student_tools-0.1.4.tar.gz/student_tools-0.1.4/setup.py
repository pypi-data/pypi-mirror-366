from setuptools import setup, find_packages

setup(
    name='student_tools',
    version='0.1.4',
    author='Error Dev',
    author_email='3rr0r.d3v@gmail.com',
    description='A collection of English, Math, and Utility tools, made for students.',
    packages=find_packages(),
    install_requires=[
        'sympy', 'collections', 're'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)