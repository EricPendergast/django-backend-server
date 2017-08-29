# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.users import User, Group

from eledata.util import from_json


# from eledata.util import to_json

# import copy
# import time


class UsersTestCase(TestCase):
    # Each element in 'users' is in the form (<login data>, <group name>)
    users = [({"username": "user1_data", "password": "asdf"}, "grp"),
             ({"username": "user2_data", "password": "sdfg"}, "oth"),
             ({"username": "user3_data", "password": "aaaa"}, "grp"), ]

    # 'admins' maps names of groups to their corresponding group admin
    admins = {}
    admin_clients = {}
    # Initializing 'admins' and 'admin_clients' so that each group name in
    # 'users' is also key in 'admins' and 'admin_clients'. This is necessary
    # for the setUp() function to work properly.
    for usr_info in users:
        admins[usr_info[1]] = None
        admin_clients[usr_info[1]] = None

    def test_create_user(self):
        c = self._create_and_login(*self.users[0])

        response = c.get("/users/index/")
        self.assertTrue(response.status_code == 200)

    def test_create_multiple_user(self):
        for user in self.users:
            self._create_and_login(*user)

        first_group = User.objects(group=Group.objects.get(name="grp"))
        # There should be three users, including the admin
        self.assertEquals(len(first_group), 3)
        self.assertTrue(first_group.filter(username=self.users[0][0]["username"]))
        self.assertTrue(first_group.filter(username=self.users[2][0]["username"]))

        second_group = User.objects(group=Group.objects.get(name="oth"))
        # There should be two users, including the admin
        self.assertEquals(len(second_group), 2)
        self.assertTrue(second_group.filter(username=self.users[1][0]["username"]))

    def test_not_logged_in(self):
        c = Client()
        response = c.get("/entity/get_all_entity/")
        self.assertEqual(response.status_code, 401)

        response = c.get("/analysis_questions/get_all_existing_analysis_questions/")
        self.assertEqual(response.status_code, 401)

    # Testing that the proper message is sent back if the user login fails due to incorrect username or password
    def test_fail_login(self):
        c = Client()
        response = c.post("/users/login/", {"username": "eric", "password": "thing"})
        self.assertEqual(response.status_code, 403)

        self.admin_clients["grp"].post("/users/create_user/", {"username": "eric", "password": "thing"})
        response = c.post("/users/login/", {"username": "eric", "password": "not the right password"})
        self.assertEqual(response.status_code, 403)

    def test_create_user_invalid_request(self):
        def assert_invalid(data, group="grp"):
            response = self.admin_clients[group].post("/users/create_user/", data)
            self.assertEquals(response.status_code, 400)

        assert_invalid({"username": "usr"})
        assert_invalid({"password": "pswrd"})
        assert_invalid({})
        # assert_invalid({"username":"usr"})
        # assert_invalid({"password":"pswrd"})

    def test_login_invalid_request(self):
        def assert_invalid(data):
            c = Client()
            response = c.post("/users/login/", data)
            self.assertEquals(response.status_code, 400)

        assert_invalid({"username": "eric"})
        assert_invalid({"password": "pswd"})

    def test_logout(self):
        user = self.users[0]
        c = self._create_and_login(*user)

        # response = c.get("/analysis_questions/get_all_existing_analysis_questions/")
        # self.assertEquals(response.status_code, 200)

        c.post("/users/logout/")

        response = c.get("/analysis_questions/get_all_existing_analysis_questions/")
        self.assertEquals(response.status_code, 401)

    def test_create_user_already_exist(self):
        response = self.admin_clients[self.users[0][1]].post("/users/create_user/", self.users[0][0])
        self.assertEquals(response.status_code, 200)

        response = self.admin_clients[self.users[0][1]].post("/users/create_user/", self.users[0][0])
        self.assertIn('error', from_json(response.content))

    def test_change_password(self):
        c = self._create_and_login(*self.users[0])
        user_info = self.users[0][0]

        response = c.post("/users/change_password/",
                          {"username": user_info['username'], "password": user_info['password'],
                           "new_password": "password1"})
        self.assertEquals(response.status_code, 200)

        response = c.post("/users/logout/", {})
        self.assertEquals(response.status_code, 200)

        response = c.post("/users/login/", {"username": user_info['username'], "password": 'password1'})
        self.assertEquals(response.status_code, 200)

    def test_change_password_invalid_input(self):
        c = self._create_and_login(*self.users[0])
        self._create_and_login(*self.users[1])
        username = self.users[0][0]['username']
        password = self.users[0][0]['password']

        def assert_invalid(data):
            response = c.post("/users/change_password/", data)
            self.assertIn("error", from_json(response.content))

        assert_invalid({"username": username + "somethingelse", "password": password, "new_password": "password1"})
        assert_invalid({"username": username, "password": password + "somethingelse", "new_password": "password1"})
        assert_invalid({"username": self.users[1][0]['username'], "password": self.users[1][0]['password'],
                       "new_password": "password1"})
        assert_invalid({"username": username, "new_password": "password1"})
        assert_invalid({"password": password, "new_password": "password1"})
        assert_invalid({"username": username, "password": password})
        assert_invalid({"new_password": "password1"})

    '''
    Testing that you need to be an admin to create a user. Make sure it fails
    for a non-admin signed in user, as well as an anonymous user.
    '''

    def test_non_admin_create_user(self):
        c = self._create_and_login(*self.users[0])
        response = c.post("/users/create_user/", {"username": "something", "password": "asdf"})
        self.assertIn('error', from_json(response.content))

        c = Client()
        response = c.post("/users/create_user/", {"username": "something", "password": "asdf"})
        self.assertIn('error', from_json(response.content))

    '''
    Creates a user with login data 'data', in group 'group_name'. Logs in to
    that user and returns the logged in client. Performs some asserts to make
    sure everything works and allow for easier debugging.
    '''

    def _create_and_login(self, data, group_name):
        c = Client()

        response = self.admin_clients[group_name].post("/users/create_user/", data)
        self.assertTrue(response.status_code == 200)

        user = User.objects.get(username=data['username'])
        self.assertTrue(user)
        self.assertTrue(user.group.name == group_name)

        response = c.post("/users/login/", data)
        self.assertTrue(response.status_code == 200)

        return c

    def setUp(self):
        # Creating an admin and group for each group name key
        for group_name in self.admins:
            self.admins[group_name] = User.create_user(username="admin" + group_name, password="pass")
            self.admins[group_name].is_group_admin = True
            self.admins[group_name].group = Group.create_group(name=group_name)
            self.admins[group_name].save()

        # Creating a signed in admin client for each group
        for group_name in self.admin_clients:
            self.admin_clients[group_name] = Client()
            self.admin_clients[group_name].post("/users/login/", {"username": "admin" + group_name, "password": "pass"})

    def doCleanups(self):
        User.drop_collection()
        Group.drop_collection()
