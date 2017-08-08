# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity
from eledata.models.users import User, Group

from eledata.util import from_json, to_json, debug_deep_print

import datetime
import platform
import time
# Create your tests here.

class EntityRollbackTestCase(TestCase):
    default_entity_data = { "id": "59560d779a4c0e4abaa1b6a8", "type": "transaction", "source_type": "local", "allowed_user": [], "created_at": "2017-06-28T14:08:10.276000", "updated_at": "2017-06-28T14:08:10.276000"}
    data_1 = [{"Transaction_ID":"1111","extra":"something"},]
    data_2 = [{"Transaction_ID":"4444","extra":"asdf"},
              {"Transaction_ID":"3333","extra":"sdfg"},]
    data_3 = [{"Transaction_ID":"4444","extra":"something"},]
    data_4 = [{"Transaction_ID":"3333","extra":"qwerty"},
              {"Transaction_ID":"6666","extra":"dog"}]
    data_5 = [{"Transaction_ID":"3333","extra":"cat"},]
    
    
    def doCleanups(self):
        Group.drop_collection()
        User.drop_collection()


    def test_replace_1(self):
        entity = self._init_entity(self.data_1)
        
        self.assertTrue(_same_elements(entity.data, self.data_1))
        entity.revert_changes(1)
        self.assertEquals(entity.data, [])
        entity.apply_changes()
        self.assertTrue(_same_elements(entity.data, self.data_1))
        entity.revert_changes()
        self.assertEquals(entity.data, [])
        
        
    def test_replace_2(self):
        entity = self._init_entity(self.data_1)
        self.assertSameElements(entity.data, self.data_1)
        
        entity.add_data(self.data_2, replace=True)
        self.assertSameElements(entity.data, self.data_2)
        
        entity.add_data(self.data_3, replace=True)
        self.assertSameElements(entity.data, self.data_3)
        
        entity.revert_changes()
        self.assertSameElements(entity.data, [])
        
        entity.apply_changes()
        self.assertSameElements(entity.data, self.data_3)
        
        entity.revert_changes(1)
        self.assertSameElements(entity.data, self.data_2)
        
        entity.revert_changes(1)
        self.assertSameElements(entity.data, self.data_1)
        
        entity.apply_changes(2)
        self.assertSameElements(entity.data, self.data_3)
        
        entity.apply_changes(2)
        self.assertSameElements(entity.data, self.data_3)
        
        
    # Testing for the correct behavior when the user rolls back changes and
    # adds new changes. All changes from after the rollback point should be
    # deleted.
    def test_overwrite(self):
        entity = self._init_entity(self.data_1)
        entity.add_data(self.data_2)
        entity.add_data(self.data_3)
        entity.add_data(self.data_4)
        entity.revert_changes(2)
        entity._check_invariants_long()
        entity.add_data(self.data_5)
        entity._check_invariants_long()
        self.assertSameElements(entity.data, [{"Transaction_ID":"1111","extra":"something"}, {"Transaction_ID":"4444","extra":"asdf"}, {"Transaction_ID":"3333","extra":"cat"},])
        
        
        entity.revert_changes()
        entity.add_data(self.data_5)
        self.assertSameElements(entity.data, self.data_5)
        # Checking that there are no future changes
        entity.apply_changes()
        self.assertSameElements(entity.data, self.data_5)
        
    
    def test_add(self):
        entity = self._init_entity(self.data_2)
        entity.add_data(self.data_3)
        
        self.assertSameElements(entity.data, [{"Transaction_ID":"3333","extra":"sdfg"}, {"Transaction_ID":"4444","extra":"something"}])
        
        entity.revert_one()
        
        self.assertSameElements(entity.data, self.data_2)
    
    
    # Testing that two users can modify an entity at the same time without
    # causing rollback issues.
    def test_concurrency_1(self):
        entity = self._init_entity(self.data_2)
        entity.add_data(self.data_3)
        entity.add_data(self.data_4)
        entity.revert_changes(2)
        # Alternate entity. Refers to the same entity in the database as
        # 'entity'
        alt_entity = Entity.objects.get(pk=entity.pk)
        
        alt_entity.apply_changes()
        alt_entity.save()
        del alt_entity
        
        # At this point, 'entity' is out of sync with its database version. The
        # database version has all changes applied, while this version is
        # reverted. When we add something, the database version should become
        # synced with this version.
        entity.add_data(self.data_5)
        
        # Check invariants to make sure entity.change_index, entity.changes,
        # and entity.data are all synced up.
        entity._check_invariants_long()
        self.assertSameElements(entity.data,
                [{"Transaction_ID":"4444","extra":"asdf"},
                 {"Transaction_ID":"3333","extra":"cat"},])
        
                
    def _init_entity(self, data):
        entity = Entity(**self.default_entity_data)
        entity.save()
        
        entity.add_data(data, replace=True)
        
        return entity
    
    
    def assertSameElements(self, list1, list2):
        self.assertTrue(_same_elements(list1, list2))
        
    
def _same_elements(list1, list2):
    for item in list1:
        if item not in list2:
            return False
    
    for item in list2:
        if item not in list1:
            return False
    
    return True
