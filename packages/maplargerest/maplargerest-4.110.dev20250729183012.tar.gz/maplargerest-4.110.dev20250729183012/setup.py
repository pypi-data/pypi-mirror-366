from setuptools import setup, find_packages # type: ignore

setup(
	packages=find_packages(exclude=("test",)),
	install_requires=[
		'python-dateutil'
	],
	setup_requires=['wheel']
)
