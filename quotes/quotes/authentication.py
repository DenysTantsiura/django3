import logging
import pathlib


key_file = 'key.txt'  # postgress

logging.basicConfig(level=logging.CRITICAL, format='%(message)s')


def watcher(function):
    def inner_eye(*args, **kwargs):
        try:
            rez = function(*args, **kwargs)

        except Exception as error:
            logging.critical(f'Something wrong!, system error:\n{error}')
            rez = f'{error}'    

        return rez
    
    return inner_eye


@watcher
def save_key(key: str, key_file: str = key_file) -> None:
    with open(key_file, 'w') as fh:
        fh.write(key)


@watcher
def load_key(key_file: str = key_file) -> str:
    with open(key_file, 'r') as fh:  # utf_8 ?
        return fh.readline().strip()  # .strip() ?


def get_password(key_file: str = key_file) -> str:
    """Return password from local file or user input in CLI."""
    if pathlib.Path(key_file).exists():
        print(f'Ok! Key-file({key_file}) found.')
        key = load_key(key_file)
        print(key)

    else:
        key: str = input('Enter the KEY:\n')
        save_key(key, key_file) if key else None
    
    return key
