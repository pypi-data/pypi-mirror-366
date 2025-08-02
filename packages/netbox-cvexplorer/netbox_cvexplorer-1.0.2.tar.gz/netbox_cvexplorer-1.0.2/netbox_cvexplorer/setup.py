from setuptools import find_packages, setup

setup(
    name='netbox-cvexplorer',
    version='1.0.2',
    description='CVE Explorer Plugin for NetBox',
    author='Tino Schiffel',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    zip_safe=False,
)
