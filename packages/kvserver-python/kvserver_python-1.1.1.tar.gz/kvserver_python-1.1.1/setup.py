from setuptools import setup, find_packages

setup(
    name="kvserver-python",
    version="1.1.1",
    packages=find_packages(
        include=["kvserver", "kvserver.*"]
    ),
    install_requires=["keyboard", "qrcode_term", "watchdog", "psutil"],
    entry_points={
        "console_scripts": [
            "kvserver = kvserver.main:main",
        ],
    },
    author="Odudu otu",
    description="A socket server that serve kivy project to kivyclient apk",
    python_requires=">=3.6",
)
