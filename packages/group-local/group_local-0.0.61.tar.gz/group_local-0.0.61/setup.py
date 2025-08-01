import setuptools  

PACKAGE_NAME = "group-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/group-local
    version='0.0.61',
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles group-local Python",
    long_description="PyPI Package for Circles group-local Python",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/group-main-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'database_mysql_local>=0.0.333',
        'logger_local>=0.0.145',
        'language_remote>=0.0.22',
        'user-context-remote>=0.0.84',
        'job-local>=0.0.3'
    ],
)
