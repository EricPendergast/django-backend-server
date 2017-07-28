# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.users import User, Group

from eledata.util import from_json, to_json


import datetime

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
        
        
    def doCleanups(self):
        User.drop_collection()
        Group.drop_collection()
