from setuptools import setup, find_packages

setup(
    name='tc2gl',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,  # Include package data
    package_data={
        '': ['templates/*.j2'],  # Include all .j2 files in the templates directory
    },
    entry_points={
        'console_scripts': [
            'tc2gl=tc2gl.cli:main',
        ],
    },
    install_requires=[
        'pandas',
        'cryptography',
        'pycparser',
        'pycryptodome',
        'PyYAML',
        'requests',
        'rsa',
        'xmltodict',
        'numpy',
        'jinja2',
        'openpyxl',
    ],
    author="Test Digital",
    author_email="info@Testdigital.com",
    description="A CLI tool to convert Teamcity pipelines to Gitlab pipelines",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://gitlab.com/Test-digital/engineering/teamcitytogitlabconverter",
)
