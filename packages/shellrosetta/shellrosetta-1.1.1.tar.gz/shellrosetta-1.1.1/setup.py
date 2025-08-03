from setuptools import setup, find_packages

setup(
    name='shellrosetta',
    version='1.1.1',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'shellrosetta=shellrosetta.cli:main',
        ],
    },
    author='David Donohue',
    author_email='david@opfynder.com',
    description='Advanced Linux/Bash to PowerShell translator with ML, plugins, web API, and interactive shell support.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sdirishguy/shellrosetta',
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: System :: Shells',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
    ],
)
