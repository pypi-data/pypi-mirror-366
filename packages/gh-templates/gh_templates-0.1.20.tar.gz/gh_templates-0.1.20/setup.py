from setuptools import setup, find_packages

setup(
    name='gh-templates',
    version='0.1.20',
    description='GitHub Templates CLI tool - unified installer',
    packages=find_packages(),
    entry_points={'console_scripts': ['gh-templates=gh_templates_unified:main']},
    license='Apache-2.0',
    install_requires=[
        'gh-templates-linux-x64-glibc==0.1.20; platform_system=="Linux" and platform_machine=="x86_64"',
        'gh-templates-linux-x64-musl==0.1.20; platform_system=="Linux" and platform_machine=="x86_64"',
        'gh-templates-linux-arm64-glibc==0.1.20; platform_system=="Linux" and platform_machine=="aarch64"',
        'gh-templates-win32-x64-msvc==0.1.20; platform_system=="Windows" and platform_machine=="AMD64"',
        'gh-templates-darwin-x64==0.1.20; platform_system=="Darwin" and platform_machine=="x86_64"',
        'gh-templates-darwin-arm64==0.1.20; platform_system=="Darwin" and platform_machine=="arm64"',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',
)
