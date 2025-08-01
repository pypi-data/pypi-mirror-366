from setuptools import setup, find_packages

setup(
    name='daraja-python',
    version='0.1.0',
    description='Reusable Django library for integrating Safaricom Daraja API (MPESA)',
    author='Fredrick Kasuku',
    author_email='fredrickasuku@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'asgiref == 3.9.1',
        'certifi == 2025.7.14',
        'charset-normalizer == 3.4.2',
        'Django == 5.2.4',
        'gunicorn==23.0.0',
        'idna == 3.10',
        'requests == 2.32.4',
        'setuptools == 80.9.0',
        'sqlparse == 0.5.3',
        'urllib3 == 2.5.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
