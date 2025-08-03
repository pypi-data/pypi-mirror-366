from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='novalang',
    version='1.0.2',
    description='NovaLang - A modern, functional programming language with premium features',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='martinmaboya',
    author_email='your@email.com',
    url='https://github.com/martinmaboya/novalang',
    packages=find_packages(),
    py_modules=[
        'main',
        'lexer', 
        'parser',
        'interpreter',
        'stdlib',
        'premium_license',
        'novalang_license',
        'payment_integration',
        'payment_server',
        'array_assign_node',
        'array_nodes',
        'for_node',
        'stdlib',
        'errors'
    ],
    entry_points={
        'console_scripts': [
            'novalang = main:main',
            'novalang-license = novalang_license:main',
            'novalang-server = payment_server:main'
        ]
    },
    install_requires=[
        'requests>=2.25.0',
    ],
    extras_require={
        'premium': [
            'cryptography>=3.0.0',
            'requests>=2.25.0',
            'stripe>=8.0.0',
            'flask>=3.0.0',
            'flask-cors>=4.0.0',
        ]
    },
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    keywords="programming-language interpreter functional-programming",
)
