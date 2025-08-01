import os
import tomllib
from pathlib import Path

import tomli_w

from umu_commander.classes import DLLOverride

CONFIG_DIR: str = os.path.join(Path.home(), ".config")
CONFIG_NAME: str = "umu-commander.toml"


class Configuration:
    PROTON_PATHS: tuple[str, ...] = (
        os.path.join(Path.home(), ".local/share/Steam/compatibilitytools.d/"),
        os.path.join(Path.home(), ".local/share/umu/compatibilitytools"),
    )
    UMU_PROTON_PATH: str = os.path.join(
        Path.home(), ".local/share/Steam/compatibilitytools.d/"
    )
    DB_NAME: str = "tracking.json"
    DB_DIR: str = os.path.join(Path.home(), ".local/share/umu/compatibilitytools")
    UMU_CONFIG_NAME: str = "umu-config.toml"
    DEFAULT_PREFIX_DIR: str = os.path.join(Path.home(), ".local/share/wineprefixes/")
    DLL_OVERRIDES_OPTIONS: tuple[DLLOverride, ...] = (
        DLLOverride("winhttp for BepInEx", "winhttp.dll=n;"),
    )

    @staticmethod
    def load():
        try:
            with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "rb") as conf_file:
                toml_conf = tomllib.load(conf_file)
                toml_conf["DLL_OVERRIDES_OPTIONS"] = tuple(
                    [
                        DLLOverride(label, override_str)
                        for label, override_str in toml_conf[
                            "DLL_OVERRIDES_OPTIONS"
                        ].items()
                    ]
                )

                for key, value in toml_conf.items():
                    setattr(Configuration, key, value)

        except FileNotFoundError:
            Configuration.dump()

    @staticmethod
    def dump():
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)

        with open(os.path.join(CONFIG_DIR, CONFIG_NAME), "wb") as conf_file:
            toml_conf = Configuration._get_attributes()
            toml_conf["DLL_OVERRIDES_OPTIONS"] = dict(
                [
                    (override.info, override.value)
                    for override in Configuration.DLL_OVERRIDES_OPTIONS
                ]
            )

            tomli_w.dump(toml_conf, conf_file)

    @staticmethod
    def _get_attributes():
        attributes = {}
        for key, value in vars(Configuration).items():
            if not key.startswith("__") and not callable(getattr(Configuration, key)):
                attributes[key] = value

        return attributes
