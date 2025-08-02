import platform
from setuptools import setup, find_packages
import os

# Get version from environment
version = os.environ.get('RELEASE_VERSION', '0.0.0')

# Determine the correct platform-specific package
def get_platform_package():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    if machine in ['x86_64', 'amd64']:
        arch = 'x64'
    elif machine in ['aarch64', 'arm64']:
        arch = 'arm64'
    elif machine in ['i386', 'i686']:
        arch = 'x86'
    else:
        arch = machine
    
    # Map to our package names
    if system == 'linux':
        if arch == 'x64':
            return 'gh-templates-linux-x64-glibc'
        elif arch == 'arm64':
            return 'gh-templates-linux-arm64-glibc'
        else:
            return f'gh-templates-linux-{arch}-glibc'
    elif system == 'darwin':
        return f'gh-templates-darwin-{arch}'
    elif system == 'windows':
        return f'gh-templates-win32-{arch}-msvc'
    else:
        # Fallback to linux x64
        return 'gh-templates-linux-x64-glibc'

platform_package = get_platform_package()

setup(
    name='gh-templates',
    version=version,
    description='GitHub Templates CLI tool - unified installer',
    long_description='''
# gh-templates

GitHub Templates CLI tool for managing and using GitHub repository templates.
This package automatically installs the correct binary for your platform.

## Usage

```bash
pip install gh-templates
gh-templates --help
```

## Supported Platforms

- Linux (x64, ARM64)
- macOS (x64, ARM64)  
- Windows (x64)
    ''',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['gh-templates=gh_templates:main']
    },
    install_requires=[
        f'{platform_package}=={version}'
    ],
    license='Apache-2.0',
    author='Rafael John',
    url='https://github.com/RafaelJohn9/gh-templates',
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
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
