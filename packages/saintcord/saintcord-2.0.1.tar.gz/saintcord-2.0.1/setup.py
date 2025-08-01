from setuptools import setup, find_packages

setup(
    name="saintcord",
    version="2.0.1",
    packages=find_packages(),
    install_requires=["discord.py"],
    author="Saint Official",
    author_email="support@saint.dev",
    description="Official @saint#7089 wrapper for Discord API.",
    python_requires=">=3.8",
)
