import json
import os
import random
import time
from datetime import datetime
from pprint import pprint
from string import ascii_letters

import allure
import pytest
import requests

from .utils.checking import Checking
from .utils.request import API


@allure.epic('Connection DB')
@allure.suite('Test Connection DB')
@allure.severity(allure.severity_level.CRITICAL)
class TestFull:
    token = None

    @allure.title('Get token.')
    def test_get_token(self, get_token):
        TestFull.token = get_token[0]
        assert TestFull.token is not None, 'Token is None.'

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('Complex')
    def complex(self):
        API.check_full_cycle(TestFull.token)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('Capacity_db')
    def capacity_db(self, connection):
        start_mb_value = API.get_profile(TestFull.token).json()['data']["content"][4][1]
        print('Db size mb:', start_mb_value)
        result_db_create = API.post_db_create(TestFull.token)
        print('Status db is :', result_db_create.json())
        db_uuid = result_db_create.json()["db_uuid"]
        print("db_uuid", db_uuid)
        time.sleep(20)
        with allure.step('Create table.'):
            query = '''
            CREATE TABLE IF NOT EXISTS accounts(
            userid INT PRIMARY KEY AUTO_INCREMENT,
            name varchar(128),
            date_of_birth datetime NULL,
            text varchar(4096),
            email varchar(128) NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            '''
        db = connection(f"{db_uuid}")
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()

        db = connection(f"{db_uuid}")
        letters = ascii_letters
        cursor = db.cursor()
        with allure.step('Insert records to the database'):
            for x in range(10):
                for i in range(10):
                    my_string = "".join(random.choice(letters) for _ in range(4096))
                    cursor.execute("""
                                    INSERT INTO accounts (name, text)
                                    VALUES (
                                    'lambotik',
                                    %(my_string)s);""",
                                   {'my_string': my_string})
                    db.commit()
                db.commit()
            cursor.execute('''select * from accounts''')
            # res = cursor.fetchall()
            # print(res)
            time.sleep(40)
        finish_mb_value = API.get_profile(TestFull.token).json()['data']["content"][4][1]
        with allure.step('Get DB size (in MB) after records have been inserted.'):
            req = requests.post('http://cisdb1.areso.pro:9090/list', json={"token": "SuperSecret"})
        pprint(req.text)
        print('Db size mb after insert:', finish_mb_value)
        create_new_db = API.post_db_create(TestFull.token)
        print(create_new_db.status_code)
        assert int(finish_mb_value) > 0, 'Value disk db used(MB) should be more than 0.'
        response_db_delete = API.delete_db(f"{db_uuid}", TestFull.token)
        Checking.check_status_code(response_db_delete, 200)


@allure.suite('GET')
class TestGET:
    token = None

    @allure.title('Get token.')
    def test_get_token(self, get_token):
        TestGET.token = get_token[0]
        assert TestGET.token is not None, 'Token is None.'

    @allure.title('GET tos.')
    def test_tos(self):
        response = API.get_tos(token=TestGET.token)
        attach = r'C:\Users\User\PycharmProjects\Oblache\tests_api\my_report.html'
        allure.attach.file(attach, name=f"Report {datetime.today()}", attachment_type=allure.attachment_type.HTML)
        Checking.check_status_code(response, 200)

    @allure.title('GET profile information.')
    def test_get_profile(self):
        response = API.get_profile(token=TestGET.token)
        Checking.check_status_code(response, 200)

    @allure.title('GET list list_dbtypes.')
    def test_get_list_db_types(self):
        response = API.get_list_db_types()
        Checking.check_status_code(response, 200)

    @allure.title('GET list db_versions.')
    def test_get_list_db_versions(self):
        response = API.get_list_dbversions()
        Checking.check_status_code(response, 200)

    @allure.title('GET list list_dbenvs.')
    def test_get_list_envs(self):
        response = API.get_list_envs()
        Checking.check_status_code(response, 200)

    @allure.title('GET list list_regions.')
    def test_get_list_regions(self):
        response = API.get_list_regions()
        Checking.check_status_code(response, 200)

    @allure.title('GET bad_request.')
    def test_get_with_bad_request(self):
        response = API.get_bad_request()
        Checking.check_status_code(response, 404)

    @allure.title('GET profile status.')
    def test_get_status(self):
        response = API.get_status(token=TestGET.token)
        Checking.check_status_code(response, 200)


@allure.suite('POST')
class TestPOST:
    token = None
    body = None
    new_password = None
    old_password = None
    email = None

    def test_get_token_and_body(self, get_token):
        TestPOST.token, TestPOST.body, TestPOST.new_password, TestPOST.old_password, TestPOST.email = get_token[0], \
            get_token[1], get_token[2], get_token[3], get_token[4]

    @allure.title('POST registration for English language.')
    def test_post_registration_for_english_language(self):
        response = API.post_registration_variety_email(
            mail=random.choice(['gmail', 'mail', 'yandex']),
            old_password=TestPOST.old_password,
            prefix=random.choice(['com', 'ru', 'by']),
            language="en-us",
            tos_agree=True)
        Checking.check_status_code(response, 201)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[1]: registered successfully')

    @allure.title('POST registration for English language not agree.')
    def test_post_registration_for_english_language_not_agree(self):
        response = API.post_registration_variety_email(
            mail=random.choice(['gmail', 'mail', 'yandex']),
            old_password=TestPOST.old_password,
            prefix=random.choice(['com', 'ru', 'by']),
            language="en-us",
            tos_agree=False)
        Checking.check_status_code(response, 400)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[36]: you must agree to Terms of Use')

    @allure.title('POST registration Bulgaria language.')
    def test_post_registration_for_bulgaria_language(self):
        response = API.post_registration_variety_email(
            mail=random.choice(['gmail', 'mail', 'yandex']),
            old_password=TestPOST.old_password,
            prefix='bg',
            language='bg-bg',
            tos_agree=True)
        Checking.check_status_code(response, 201)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[1]: регистриран успешно на потребитель')

    @allure.title('POST registration Bulgaria language not agree.')
    def test_post_registration_for_bulgaria_language_not_agree(self):
        response = API.post_registration_variety_email(
            mail=random.choice(['gmail', 'mail', 'yandex']),
            old_password=TestPOST.old_password,
            prefix='bg',
            language='bg-bg',
            tos_agree=False)
        Checking.check_status_code(response, 400)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[36]: трябва да се съгласите с Условията за Ползване')

    @allure.title('POST registration email is taken for en-us')
    def test_post_registration_email_is_taken_for_en_en(self):
        response = API.post_registration(
            email=TestPOST.email,
            old_password=TestPOST.old_password,
            language="en-us",
            tos_agree=True)
        Checking.check_status_code(response, 400)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[3]: registration failed, this email is taken')

    @allure.title('POST registration email is taken for bg-bg')
    def test_post_registration_email_is_taken_for_bg_bg(self):
        response = API.post_registration(
            email=TestPOST.email,
            old_password=TestPOST.old_password,
            language="bg-bg",
            tos_agree=True)
        Checking.check_status_code(response, 400)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[3]: неуспешна регистрация на потребител, имейлът е зает')

    @allure.title('POST registration email is taken for unsupported languages')
    def test_post_registration_email_is_taken_for_unsupported_languages(self):
        response = API.post_registration(
            email=TestPOST.email,
            old_password=TestPOST.old_password,
            language="ru-ru",
            tos_agree=True)
        status_code = response
        Checking.check_status_code(status_code, 400)
        Checking.check_json_search_word_in_value(
            response, 'content', 'msg[34]: the language is not accepted')

    @allure.title('POST login')
    def test_post_login(self):
        response = API.post_login(body=TestPOST.body)
        Checking.check_status_code(response, 200)

    @allure.title('POST is logged')
    def test_post_is_logged(self):
        response = API.post_is_logged(token=TestPOST.token)
        Checking.check_status_code(response, 200)

    @allure.title('POST is_logged_with_wrong_token')
    def test_post_is_logged_with_wrong_token(self):
        response = API.post_is_logged_with_wrong_token()
        Checking.check_status_code(response, 401)

    @allure.title('POST db_create')
    def test_post_db_create(self):
        response = API.post_db_create(token=TestPOST.token)
        Checking.check_status_code(response, 201)

    @allure.title('POST db_create_with_wrong_db_type.')
    def test_post_db_create_with_wrong_values_dbtype(self):
        response_db_list = API.post_db_create_wrong_value_db_type(token=TestPOST.token)
        Checking.check_status_code(response_db_list, 400)
        Checking.check_json_search_word_in_value(
            response_db_list, "content",
            "error: DB type isn't found or isn't available for order")

    @allure.title('POST db_create_with_wrong_db_version.')
    def test_post_db_create_with_wrong_values_db_version(self):
        response_db_list = API.post_db_create_wrong_value_db_version(token=TestPOST.token)
        Checking.check_status_code(response_db_list, 400)
        Checking.check_json_search_word_in_value(
            response_db_list, "content",
            "error: DB version isn't found or isn't available for order")

    @allure.title('POST db_create_with_wrong_env.')
    def test_post_db_create_with_wrong_values_env(self):
        response_db_list = API.post_db_create_wrong_value_env(token=TestPOST.token)
        Checking.check_status_code(response_db_list, 400)
        Checking.check_json_search_word_in_value(
            response_db_list, "content",
            "error: DB environment isn't found or isn't available for order")

    @allure.title('POST db_create_with_wrong_region.')
    def test_post_db_create_with_wrong_values_region(self):
        response_db_list = API.post_db_create_wrong_value_region(token=TestPOST.token)
        Checking.check_status_code(response_db_list, 400)
        Checking.check_json_search_word_in_value(
            response_db_list, "content",
            "error: region isn't found or isn't available for order")

    @allure.title('POST db_list')
    def test_post_db_list(self):
        response_db_list = API.post_db_list(token=TestPOST.token)
        Checking.check_status_code(response_db_list, 200)

    @allure.title('POST container_list')
    def test_post_container_list(self):
        result = API.post_container_list(token=TestPOST.token)
        Checking.check_status_code(result, 200)

    @allure.title('POST db_list_with_filter')
    @pytest.mark.xfail(reason='There are databases that need to be deleted manually.')
    def test_post_db_list_with_filter(self):
        list_db = API.post_db_list(token=TestPOST.token)
        json_list_db = json.loads(list_db.text)
        try:
            first_db_uuid = list(json_list_db['data'])[-1]
            response_db_list = API.delete_db(uuid=first_db_uuid, token=TestPOST.token)
            Checking.check_status_code(response_db_list, 200)
        except IndexError as ex:
            print(ex)
            assert str(ex) == 'list index out of range', 'Db list is empty.'

    @allure.title('POST change_password')
    def test_post_change_password(self):
        new_password = TestPOST.new_password
        response_change_password = API.post_change_password(
            token=TestPOST.token,
            old_password=TestPOST.new_password,
            new_password=new_password)
        Checking.check_status_code(response_change_password, 200)
        Checking.check_json_search_word_in_value(response_change_password, "content",
                                                 "msg[31]: password successfully updated")
        response_change_password = API.post_change_password(
            token=TestPOST.token,
            old_password=new_password,
            new_password=TestPOST.new_password)
        Checking.check_status_code(response_change_password, 200)
        Checking.check_json_search_word_in_value(response_change_password, "content",
                                                 "msg[31]: password successfully updated")

    @allure.title('POST change_password_with_wrong_data')
    def test_post_change_password_with_wrong_data(self):
        result = API.post_change_password(
            token=TestPOST.token,
            old_password='123456',
            new_password='123456')
        Checking.check_status_code(result, 400)
        Checking.check_json_search_word_in_value(
            result, 'content', 'msg[7]: error: current password is incorrect')

    @allure.title('POST change_password_without_token')
    def test_post_change_password_without_token(self):
        new_password = TestPOST.new_password
        result = API.post_change_password(
            token='1',
            old_password=TestPOST.new_password,
            new_password=new_password)
        Checking.check_status_code(result, 401)
        Checking.check_json_search_word_in_value(result, 'content', 'msg[5]: unauthenticated')

    @allure.title('POST create_docker_container')
    def test_post_container_list(self):
        result = API.post_container_list(token=TestPOST.token)
        Checking.check_status_code(result, 200)

    @allure.title('POST create_docker_container')
    def test_post_create_docker_container(self):
        amount_before = API.post_container_list(token=TestPOST.token)
        result = API.post_create_docker_container(token=TestPOST.token)
        amount_after = API.post_container_list(token=TestPOST.token)
        Checking.check_status_code(result, 201)
        Checking.check_json_value(result, 'msg', 'order for new container accepted')
        assert len(amount_before.json()['data']) + 1 == len(amount_after.json()['data']), \
            'Container not added to table.'

    @allure.title('POST checking ports_len positive')
    def test_post_checking_ports_len_positive(self):
        result = API.post_create_docker_container_checking_ports(
            token=TestPOST.token,
            port_len="80-89")
        Checking.check_status_code(result, 201)
        Checking.check_json_value(result, 'msg', 'order for new container accepted')

    @allure.title('POST checking ports_len negative range')
    def test_post_checking_ports_len_negative_range(self):
        result = API.post_create_docker_container_checking_ports(
            token=TestPOST.token,
            port_len="80-90")
        Checking.check_status_code(result, 400)
        Checking.check_json_value(result, 'msg', 'msg[]: ports range is too wide')

    @allure.title('POST checking ports_len negative len')
    def test_post_checking_ports_len_negative_len(self):
        result = API.post_create_docker_container_checking_ports(
            token=TestPOST.token,
            port_len="80,81,82,83,84,85,86,87,88,89,90")
        Checking.check_status_code(result, 400)
        Checking.check_json_value(result, 'msg', 'msg[]: ports range is too wide')

    @allure.title('POST checking ports_len negative symbols')
    def test_post_checking_ports_len_negative_symbols(self):
        result = API.post_create_docker_container_checking_ports(
            token=TestPOST.token,
            port_len="qwert")
        Checking.check_status_code(result, 400)
        Checking.check_json_value(result, 'msg', "msg[]: ports range isn't accepted")

    @allure.title('POST create_docker_container_without_token')
    def test_post_create_docker_container_without_token(self):
        result = API.post_create_docker_container(token='incorrect_token')
        Checking.check_status_code(result, 401)
        Checking.check_json_value(result, 'msg', 'msg[5]: unauthenticated')

    @allure.title('POST create_docker_container_without_token')
    def test_post_create_docker_with_defunct_image(self):
        result = API.post_create_docker_container_with_defunct_image(token=TestPOST.token)
        Checking.check_status_code(result, 400)
        Checking.check_json_value(result, 'msg', "msg[]: the image doesn't found in the DockerHub")

    @allure.title('POST delete_container')
    def test_delete_container(self):
        result = API.post_delete_docker_container(
            token=TestPOST.token,
            list_index=-1)
        Checking.check_status_code(result, 200)

    @allure.title('POST delete_db')
    @pytest.mark.xfail(reason='When using this method during a test run, the database may be in deleting status.')
    def test_delete_db(self):
        list_db = API.post_db_list(token=TestPOST.token)
        json_list_db = json.loads(list_db.text)
        try:
            first_db_uuid = list(json_list_db['data'])[0]
            response_db_delete = API.delete_db(
                uuid=first_db_uuid,
                token=TestPOST.token)
            Checking.check_status_code(response_db_delete, 200)
        except IndexError as ex:
            print(ex)
            assert str(ex) == 'list index out of range', 'Db list is empty.'

    @pytest.mark.xfail(
        reason="If databases will be deleting more than 1 minute and all databases won't deleting for this time.")
    @allure.title('POST delete_all_created_db')
    def test_delete_all_created_db(self):
        json_list_db = API.delete_all_created_db(token=TestPOST.token)
        list_db = API.post_db_list(token=TestPOST.token)
        Checking.check_status_code(list_db, 200)
        assert json_list_db == {}
