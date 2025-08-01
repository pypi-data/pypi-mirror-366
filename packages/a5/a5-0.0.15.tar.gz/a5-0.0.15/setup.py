import setuptools

with open("a5/version") as f:
    version = f.read().strip()

setuptools.setup(
    name="a5",
    version=version,
    author="Aapeli",
    description="a5",
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    package_data={"a5": ["version"]},
    python_requires=">=3.9",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["boto3", "gunicorn", "openai", "pico-acme", "pynacl", "tqdm"],
)
