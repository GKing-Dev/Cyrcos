from setuptools import setup

setup(
	name = "Cyrcos",
	description = "A Circos-like implementation in Python 3 using Matplotlib",
	version = "1.0",
	author = "Greg King",
	author_email = "greg@king-dev.com",
	packages = ["Cyrcos"],
	install_requires = ["matplotlib", "numpy"],
	licence = "MIT",
	url = "https://github.com/GKing-Dev/Cyrcos",
	keywords = "Circos matplotlib chord graph visualization graphics"
)
