import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
import time
from network.models import Post, User, UserFollowing
from django.test import TestCase, Client
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PythonOrgSearch(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()


    def test_register(self):

        self.driver.get('%s%s' % (self.live_server_url, '/'))
        self.driver.find_element_by_id('register').click()
        self.driver.find_element_by_id('username').send_keys('TestUser1')
        self.driver.find_element_by_id('password').send_keys('123taz@111')
        self.driver.find_element_by_id('password_confirm').send_keys('123taz@111')
        self.driver.find_element_by_id('email').send_keys('1234@mail.ru')

        self.driver.find_element_by_id('btn_register').click()
        user = User.objects.get(username='TestUser1')
        print(user, 'user')
        print(user.is_active, 'userpoiuouUPIUO')
        print(User.objects.all(), 'allObjects')
        assert self.driver.find_element_by_id('name_user').text == 'TestUser1'
        assert user.username == 'TestUser1'

    def test_logout(self):
        self.driver.get('%s%s' % (self.live_server_url, '/'))
        self.driver.find_element_by_id('register').click()
        self.driver.find_element_by_id('username').send_keys('TestUser1')
        self.driver.find_element_by_id('password').send_keys('123taz@111')
        self.driver.find_element_by_id('password_confirm').send_keys('123taz@111')
        self.driver.find_element_by_id('email').send_keys('1234@mail.ru')
        self.driver.find_element_by_id('btn_register').click()
        user = User.objects.get(username='TestUser1')
        assert self.driver.find_element_by_id('name_user').text == 'TestUser1'
        assert user.username == 'TestUser1'

        self.driver.find_element_by_id('logout').click()
        assert self.driver.find_element_by_id('login') != None


    def test_login(self):
        self.driver.get('%s%s' % (self.live_server_url, '/'))
        self.driver.find_element_by_id('register').click()
        self.driver.find_element_by_id('username').send_keys('TestUser1')
        self.driver.find_element_by_id('password').send_keys('123taz@111')
        self.driver.find_element_by_id('password_confirm').send_keys('123taz@111')
        self.driver.find_element_by_id('email').send_keys('1234@mail.ru')
        self.driver.find_element_by_id('btn_register').click()
        user = User.objects.get(username='TestUser1')
        assert self.driver.find_element_by_id('name_user').text == 'TestUser1'
        assert user.username == 'TestUser1'

        self.driver.find_element_by_id('logout').click()
        assert self.driver.find_element_by_id('login') != None

        self.driver.find_element_by_id('login').click()
        self.driver.find_element_by_id('username').send_keys('TestUser1')
        self.driver.find_element_by_id('password').send_keys('123taz@111')
        self.driver.find_element_by_id('btn_login').click()

        assert self.driver.find_element_by_id('name_user').text == 'TestUser1'


    def test_username_link(self):
        self.driver.get('%s%s' % (self.live_server_url, '/'))
        self.driver.find_element_by_id('register').click()
        self.driver.find_element_by_id('username').send_keys('TestUser1')
        self.driver.find_element_by_id('password').send_keys('123taz@111')
        self.driver.find_element_by_id('password_confirm').send_keys('123taz@111')
        self.driver.find_element_by_id('email').send_keys('1234@mail.ru')
        self.driver.find_element_by_id('btn_register').click()
        user = User.objects.get(username='TestUser1')
        assert self.driver.find_element_by_id('name_user').text == 'TestUser1'
        assert user.username == 'TestUser1'

        profile_link = self.driver.find_element_by_id('user_info')
        profile_link.click()
        user_link = self.driver.find_element_by_id('username_info')

        assert profile_link.get_attribute('value') == user_link.get_attribute('value')




    def tearDown(self):
        self.driver.close()

    if __name__ == "__main__":
        unittest.main()



