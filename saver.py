#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from os.path import exists
from manager.save import SaveManager

CONFIG_FILE_PATH: str = 'config.json'


def main() -> None:
    """

    :return:
    """
    if exists(CONFIG_FILE_PATH):
        data = None
        with open(CONFIG_FILE_PATH) as json_file:
            data = json.load(json_file)
        if data:
            save_manager = SaveManager()
            save_manager.run(config=data, save_cache_size=100, saver_process_count=1)

    else:
        print('config.txt is required')


if __name__ == "__main__":
    main()
