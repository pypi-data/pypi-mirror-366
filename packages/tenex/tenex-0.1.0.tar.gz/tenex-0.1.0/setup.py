import setuptools

with open("./README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="tenex",
    version="0.1.0",
    author="tenex",
    author_email="lihongzhang@bytedance.com",
    description="The better way to handle ndarray and train model.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lihz6/tenex",
    packages=setuptools.find_packages(),
    # 3.7+: **kwargs确保有序
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*
