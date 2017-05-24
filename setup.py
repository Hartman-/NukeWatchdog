import setuptools

setuptools.setup(
    name="NukeWatchdog",
    version="0.1.0",
    url="github.com/Hartman-/NukeWatchdog",

    author="Ian Hartman",
    author_email="ian.hartman95@gmail.com",

    description="Watch-folder solution for submitting renders to a local queue a for rendering.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
