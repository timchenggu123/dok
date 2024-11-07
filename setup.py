import setuptools

with open('readme.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='hako',
    version='0.0.0',
    author='Tim-Cheng Gu',
    author_email='2013tim.g@gmail.com',
    description='Quickly start your containerized dev environment.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    package_dir={
        "hako": "src/hako"
    },
    entry_points={
        'console_scripts': [
            'hako=hako.cli:main',
        ]
    },
    keywords='Docker utility tool',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ]
)