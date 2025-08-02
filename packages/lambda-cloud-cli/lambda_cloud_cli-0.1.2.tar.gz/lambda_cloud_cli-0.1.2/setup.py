from setuptools import setup

setup(
    name='lambda-cloud-cli',
    version='0.1.2',
    description='CLI tool for managing Lambda Cloud resources',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Taylor Gautreaux',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/lambda-cli',
    license='MIT',
    py_modules=['lambda_cli', 'lambda_api_client', 'config'],
    install_requires=[
    'typer',
    'requests',
    'rich',
    'shellingham',
    ],
    entry_points={
        'console_scripts': [
            'lambda-cli=lambda_cli:app',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

