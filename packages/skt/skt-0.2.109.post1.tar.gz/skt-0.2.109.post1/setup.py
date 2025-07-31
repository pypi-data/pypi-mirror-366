import setuptools


def load_long_description():
    with open("README.md", "r") as f:
        long_description = f.read()
    return long_description


# Start dependencies group
air = [
    "bayesian-optimization",
    "catboost",
    "plotnine",
    "shap",
    "gensim",
    "seaborn",
    "scikit-learn",
    "scipy",
    "lifelines",
    "xgboost",
    "lightgbm",
    "implicit",
    "matplotlib",
    "mushroom_rl",
    "pytorch-widedeep",
    "RL-for-reco",
    "LightGBMwithBayesOpt",
    "tensorboardX",
    "torchsummary",
    "pycaret",
    "openpyxl>=3.0.0",
    "netcal",
    "haversine",
    "pyfarmhash",
    "mabalgs",
]

setuptools.setup(
    name="skt",
    version="0.2.109.post1",
    author="SKT",
    author_email="all@sktai.io",
    description="SKT package",
    long_description=load_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/sktaiflow/skt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "streamz",
        "confluent-kafka",
        "thrift-sasl",
        "hvac>=0.9.6",
        "pyarrow",
        "numpy",
        "pandas",
        "slackclient>=2.5.0",
        "httplib2>=0.18.0",
        "click",
        "PyGithub",
        "pycryptodome",
        "tabulate>=0.8.7",
        "pandas_gbq>=0.13.2",
        "google-cloud-bigquery-storage",
        "grpcio<2.0dev",
        "sqlalchemy>=1.3.18",
        "packaging",
        "tqdm>=4.48.2",
        "ipywidgets",
        "hmsclient-hive-3",
        "google-cloud-monitoring",
        "redis",
        "pyathena",
        "opensearch-py",
        "requests_aws4auth",
        "google-auth-httplib2",
        "google-api-python-client",
        "pydata-google-auth",
        "jupysql",
    ],
    entry_points={"console_scripts": ["nes = skt.nes:nes_cli"]},
    extras_require={"air": air},
)
