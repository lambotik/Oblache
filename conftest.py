import os

import requests
from dotenv import load_dotenv

from tests_api.utils.checking import Checking
import logging
import allure
import pytest


class AllureHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        with allure.step(log_entry):
            pass


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    # Инициализация логгера
    allure_handler = AllureHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    allure_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(allure_handler)


base_url = 'https://dbend.areso.pro'  # Base url


@pytest.fixture()
def get_token():
    """
    Method return:\n
    token: str\n
    body: dict\n
    new_password: str\n
    old_password: str\n
    email: str
    :returns: token: str, body: dict, new_password: str, old_password:str, email: str
    """
    load_dotenv()
    email = os.getenv('EMAIL')
    old_password = os.getenv('PASSWORD')
    new_password = '123456789'
    try:
        body = {"email": email, "password": f'{old_password}'}
        result = requests.post('https://dbend.areso.pro/login', json=body)
        token = result.json()['token']
        if token != {}:
            new_password, old_password = old_password, new_password
        Checking.check_status_code(result, 200)
        return token, body, new_password, old_password, email
    except Exception as ex:
        print(ex)
        old_password, new_password = new_password, old_password
        body = {"email": email, "password": f'{old_password}'}
        result = requests.post('https://dbend.areso.pro/login', json=body)
        token = result.json()['token']
        Checking.check_status_code(result, 200)
        return token, body, new_password, old_password, email


@pytest.fixture()
def get_token_backup_1():
    """
    Method return:\n
    token: str\n
    body: dict\n
    uuid: str
    """
    load_dotenv()
    email = os.getenv('BACKUP1_MAIL')
    old_password = os.getenv('BACKUP1_PASSWORD')
    uuid = os.getenv('BACKUP1_UUID')
    body = {"email": email, "password": old_password}
    result = requests.post('https://dbend.areso.pro/login', json=body)
    Checking.check_status_code(result, 200)
    token = result.json()['token']
    return token, body, uuid


@pytest.fixture()
def get_token_backup_2():
    """
    Method return:\n
    token: str\n
    body: dict\n
    uuid: str
    """
    load_dotenv()
    email = os.getenv('BACKUP2_MAIL')
    old_password = os.getenv('BACKUP2_PASSWORD')
    uuid = os.getenv('BACKUP2_UUID')
    body = {"email": email, "password": old_password}
    result = requests.post('https://dbend.areso.pro/login', json=body)
    Checking.check_status_code(result, 200)
    token = result.json()['token']
    return token, body, uuid
