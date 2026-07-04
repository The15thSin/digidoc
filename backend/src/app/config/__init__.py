import os
import yaml
from pathlib import Path

ENV = os.getenv("ENV")

if not ENV:
    raise ValueError("Environment variable 'ENV' is not set.")

CONFIG_PATH = Path(f"src/app/config/config.{ENV}.yaml")

with open(CONFIG_PATH, "r") as cfg_file:
    config = yaml.safe_load(cfg_file)