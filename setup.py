from setuptools import setup

setup(
    name="netbox_importer",
    version="0.3.2",
    description="Manage your Pikett Team using this fancy CLI Tool",
    url="https://git.adfinis-sygroup.ch/ad-sy/monitoring-change-pikett",
    author="Philipp Marmet, Cyrill von Wattenwyl",
    license="AGPL-3.0",
    packages=["netbox_importer"],
    data_files = [('/etc/netbox_importer', ['netbox_importer/config/config.yaml.example'])],
    # install_requires=requirements,
    zip_safe=False,
    entry_points={"console_scripts": ["netbox_importer=netbox_importer.main:main"]},
)

