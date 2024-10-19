#!/usr/bin/env python3
from hashlib import md5
from os import path, remove
from pathlib import Path
from random import randint
from subprocess import run
from typing import List

CLI = '/opt/mailinabox/management/cli.py'
OUTPUT_FILE = '.created-list'


def asset_cli_exists():
    if not path.isfile(CLI):
        raise FileNotFoundError('[%s] does not exist. Is MIAB installed?' % CLI)


def get_email_address_list() -> List[str]:
    try:
        asset_cli_exists()
        result = run([CLI, 'user'], capture_output=True, check=True)
        if result.stderr:
            raise ValueError(result.stderr)
        return [address.strip().rstrip('*') for address in result.stdout.decode('utf-8').split()]
    except OSError as error:
        print('ERROR while fetching email list: %s' % error)

    return []


def create_email_address(email_address: str):
    md5_hash = md5()
    md5_hash.update(email_address.encode('utf-8'))
    password = '%s%s' % (randint(999999, 9999999), md5_hash.hexdigest())

    try:
        asset_cli_exists()
        print('Creating %s' % email_address)
        result = run([CLI, 'user', 'add', email_address, password], capture_output=True, check=True)
        if result.stderr:
            raise ValueError(result.stderr)
        with open(OUTPUT_FILE, 'a') as output:
            output.write('%s %s \n' % (email_address, password))
    except OSError as error:
        print('ERROR while creating email address(%s) : %s' % (email_address, error))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create an MIAB (Mail-in-a-box) email address for each line found in source list. The list of created users and passwords is added toa new file '.created-list' in the current working directory ")
    parser.add_argument("--source",
                        required=True,
                        help="Source file containing email address to create",
                        type=argparse.FileType())
    arguments = parser.parse_args()

    if path.exists(OUTPUT_FILE):
        remove(OUTPUT_FILE)
    Path(OUTPUT_FILE).touch()

    existing_addresses = get_email_address_list()

    for _line in arguments.source:
        email_address = _line.strip()

        if email_address in existing_addresses:
            print('%s already exists ...' % email_address)
            continue

        create_email_address(email_address)

    arguments.source.close()
