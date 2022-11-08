import codecs

import setuptools


setuptools.setup(
    # general description
    name='zerospeech-benchmark',
    description="Toolset for usage of the Zero Resource Challenge Benchmarks",
    # python package dependencies
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    # include Python code
    packages=setuptools.find_packages(),
    zip_safe=False,
    # the command-line scripts to export
    entry_points={
        'console_scripts': [
            'zrc        = zerospeech.startup:main'
        ]
    },

    # metadata
    author='CoML team',
    author_email='dev@zerospeech.com',
    license='GPL3',
    url='https://zerospeech.com/2021',
    long_description=codecs.open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
)
