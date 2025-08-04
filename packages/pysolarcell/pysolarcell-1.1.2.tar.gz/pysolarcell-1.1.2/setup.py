import setuptools

with open('README.md', 'r') as f:
    longDescription = f.read()

setuptools.setup(
    name='pysolarcell',
    version='1.1.2',
    author='AustL',
    author_email='21chydra@gmail.com',
    description='Solar cell simulation software',
    long_description=longDescription,
    long_description_content_type='text/markdown',
    url='https://github.com/AustL/PySolarCell',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.12',
    license='MIT',
    install_requires=['sympy', 'numpy', 'pandas', 'matplotlib', 'scipy'],
    include_package_data=True,
    package_data={
            'pysolarcell': ['materials/*', 'spectra/*'],
    },
)
