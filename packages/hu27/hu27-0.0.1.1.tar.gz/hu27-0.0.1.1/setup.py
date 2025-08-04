from setuptools import setup, find_packages

setup(
    name='hu27',
    version='0.0.1.1',
    author='hu27',
    author_email='',
    description="hu27!",
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
    entry_points={
    },
)
