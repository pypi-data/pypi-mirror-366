import setuptools

PACKAGE_NAME = "data-source-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/data-source-local
    version='0.0.17',
    author="Circles",
    author_email="info@circles.ai",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description=PACKAGE_NAME,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'logger-local>=0.0.60',
        'database-mysql-local>=0.0.83',
        'language-remote',
    ],
)
