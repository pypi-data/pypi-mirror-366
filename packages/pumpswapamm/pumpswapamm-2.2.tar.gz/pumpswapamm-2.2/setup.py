#  ─── PumpSwapAMM/setup.py ──────────────────────────────────────────────────
from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
setup(
    name            = "pumpswapamm",
    version         = "2.2",
    description     = "Python SDK for Pump.fun’s PumpSwap AMM on Solana",
    long_description= (this_dir / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author          = "FLOCK4H",
    license         = "MIT",
    python_requires = ">=3.10",
    packages=["pumpswapamm"],
    package_dir={
        "pumpswapamm": "pumpswapamm",
    },
    include_package_data = True,
    install_requires=[
        "solana==0.35.1",          # RPC client + spl-token helpers
        "solders==0.21.0",         # Rust bindings – signatures / PDAs
        "construct",         # binary layout parsing
        "base58",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)