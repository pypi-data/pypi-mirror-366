import json
import os
from collections import defaultdict

from umu_commander.configuration import Configuration as config


class Database:
    _db: defaultdict[str, defaultdict[str, list[str]]]

    @staticmethod
    def load():
        if not os.path.exists(config.DB_DIR):
            os.mkdir(config.DB_DIR)

        try:
            with open(os.path.join(config.DB_DIR, config.DB_NAME), "rt") as db_file:
                Database._db = defaultdict(lambda: defaultdict(list))
                Database._db.update(json.load(db_file))

        except FileNotFoundError:
            Database._db = defaultdict(lambda: defaultdict(list))

    @staticmethod
    def dump():
        with open(os.path.join(config.DB_DIR, config.DB_NAME), "wt") as db_file:
            # noinspection PyTypeChecker
            json.dump(Database._db, db_file, indent="\t")

    @staticmethod
    def get(
        proton_dir: str = None, proton_ver: str = None
    ) -> dict[str, dict[str, list[str]]] | dict[str, list[str]] | list[str]:
        if proton_dir is None and proton_ver is None:
            return Database._db

        if proton_ver is None:
            return Database._db[proton_dir]

        if proton_ver not in Database._db[proton_dir]:
            Database._db[proton_dir][proton_ver] = []

        return Database._db[proton_dir][proton_ver]
