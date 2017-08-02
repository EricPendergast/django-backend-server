# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.users import User, Group

from eledata.util import from_json, to_json

import copy

class UsersTestCase(TestCase):
    users = [({"username":"user1_data", "password":"asdf", "group":"grp"}, {"username":"user1_data", "password":"asdf"}),
             ({"username":"user2_data", "password":"sdfg", "group":"oth"}, {"username":"user2_data", "password":"sdfg"}),
             ({"username":"user3_data", "password":"aaaa", "group":"grp"}, {"username":"user3_data", "password":"aaaa"}),]
            
    
    def test_create_user(self):
        self._test_create_and_login(*self.users[0])
        
        
    def test_create_multiple_user(self):
        for user in self.users:
            self._test_create_and_login(*user)

        first_group = User.objects(group=Group.objects.get(name="grp"))
        self.assertEquals(len(first_group), 2)
        self.assertTrue(first_group.filter(username=self.users[0][0]["username"]))
        self.assertTrue(first_group.filter(username=self.users[2][0]["username"]))


        second_group = User.objects(group=Group.objects.get(name="oth"))
        self.assertEquals(len(second_group), 1)
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
        response = c.post("/users/login/", {"username":"eric", "password":"thing"})
        self.assertEqual(response.status_code, 403)
        
        c.post("/users/create_user/", {"username":"eric", "password":"thing", "group":"grp"})
        response = c.post("/users/login/", {"username":"eric", "password":"not the right password"})
        self.assertEqual(response.status_code, 403)
    
    
    def test_create_user_invalid_request(self):
        def assert_invalid(data):
            c = Client()
            response = c.post("/users/create_user/", data)
            self.assertEquals(response.status_code, 400)
            
        assert_invalid({"username":"usr"})
        assert_invalid({"password":"pswrd"})
        assert_invalid({"group":"grp"})
        assert_invalid({"username":"usr", "group":"grp"})
        assert_invalid({"password":"pswrd", "group":"grp"})
        assert_invalid({"username":"usr", "password":"pswrd"})
            
            
    def test_login_invalid_request(self):
        def assert_invalid(data):
            c = Client()
            response = c.post("/users/login/", data)
            self.assertEquals(response.status_code, 400)
        
        assert_invalid({"username":"eric"})
        assert_invalid({"password":"pswd"})
    
    
    def test_logout(self):
        user = self.users[0]
        c = self._test_create_and_login(*user)
        
        # response = c.get("/analysis_questions/get_all_existing_analysis_questions/")
        # self.assertEquals(response.status_code, 200)
        
        c.post("/users/logout/")
        
        response = c.get("/analysis_questions/get_all_existing_analysis_questions/")
        self.assertEquals(response.status_code, 401)
    
    
    def test_create_user_already_exist(self):
        c = Client()
        response = c.post("/users/create_user/", self.users[0][0])
        self.assertEquals(response.status_code, 200)
        
        response = c.post("/users/create_user/", self.users[0][0])
        self.assertIn('error', from_json(response.content))
        
        
    def test_change_password(self):
        c = self._test_create_and_login(*self.users[0])
        user_info = self.users[0][0]
        
        
        response = c.post("/users/change_password/", {"username":user_info['username'], "password":user_info['password'], "new_password":"password1"})
        self.assertEquals(response.status_code, 200)
        
        response = c.post("/users/logout/", {})
        self.assertEquals(response.status_code, 200)
        
        response = c.post("/users/login/", {"username":user_info['username'], "password":'password1'})
        self.assertEquals(response.status_code, 200)
        
    
    def test_change_password_invalid_input(self):
        c = self._test_create_and_login(*self.users[0])
        self._test_create_and_login(*self.users[1])
        username = self.users[0][0]['username']
        password = self.users[0][0]['password']
        def assertInvalid(client, data):
            response = c.post("/users/change_password/", data)
            self.assertIn("error", from_json(response.content))
            
        assertInvalid(c, {"username":username+"somethingelse", "password":password, "new_password":"password1"})
        assertInvalid(c, {"username":username, "password":password+"somethingelse", "new_password":"password1"})
        assertInvalid(c, {"username":self.users[1][0]['username'], "password":self.users[1][0]['password'], "new_password":"password1"})
        assertInvalid(c, {"username":username, "new_password":"password1"})
        assertInvalid(c, {"password":password, "new_password":"password1"})
        assertInvalid(c, {"username":username, "password":password})
        assertInvalid(c, {"new_password":"password1"})
        
        
    def _test_create_and_login(self, data, login_data):
        c = Client()
        response = c.post("/users/create_user/", data)
        self.assertTrue(response.status_code == 200)
        
        user = User.objects.get(username=data['username'])
        self.assertTrue(user)
        self.assertTrue(user.group.name == data['group'])
        
        # import pdb; pdb.set_trace()
        response = c.post("/users/login/", login_data)
        self.assertTrue(response.status_code == 200)
        
        response = c.get("/users/index/")
        self.assertTrue(response.status_code == 200)
        
        return c
        
    def doCleanups(self):
        User.drop_collection()
        Group.drop_collection()
