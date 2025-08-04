from setuptools import setup, find_packages

setup(
    name="oda-utils",  
    version="0.1.0",
    description="Herramientas inteligentes para bots de Discord: Anti-Raid, Embeds y más.",
    author="maestro._.oda",
    packages=find_packages(),
    install_requires=["discord.py>=2.3.2"],  
    python_requires=">=3.8",
)
