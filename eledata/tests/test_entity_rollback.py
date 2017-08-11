# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from eledata.models.entity import Entity
from eledata.models.users import User, Group

from eledata.util import from_json, to_json, debug_deep_print, get_time

import datetime
import platform
import time
# Create your tests here.

class EntityRollbackTestCase(TestCase):
    default_entity_data = { "id": "59560d779a4c0e4abaa1b6a8", "type": "transaction", "source_type": "local", "allowed_user": [], "created_at": "2017-06-28T14:08:10.276000", "updated_at": "2017-06-28T14:08:10.276000", "state":0}
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
        
        entity.add_change(self.data_2, replace=True)
        self.assertSameElements(entity.data, self.data_2)
        
        entity.add_change(self.data_3, replace=True)
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
        entity.add_change(self.data_2)
        entity.add_change(self.data_3)
        entity.add_change(self.data_4)
        entity.revert_changes(2)
        entity._check_invariants_long()
        entity.add_change(self.data_5)
        entity._check_invariants_long()
        self.assertSameElements(entity.data, [{"Transaction_ID":"1111","extra":"something"}, {"Transaction_ID":"4444","extra":"asdf"}, {"Transaction_ID":"3333","extra":"cat"},])
        
        
        entity.revert_changes()
        entity.add_change(self.data_5)
        self.assertSameElements(entity.data, self.data_5)
        # Checking that there are no future changes
        entity.apply_changes()
        self.assertSameElements(entity.data, self.data_5)
        
    
    def test_add(self):
        entity = self._init_entity(self.data_2)
        entity.add_change(self.data_3)
        
        self.assertSameElements(entity.data, [{"Transaction_ID":"3333","extra":"sdfg"}, {"Transaction_ID":"4444","extra":"something"}])
        
        entity.revert_one()
        
        self.assertSameElements(entity.data, self.data_2)
        
        
    # Testing that util.get_time() is monotonic
    def test_get_time(self):
        for i in range(100):
            t1 = get_time()
            t2 = get_time()
            
            self.assertLessEqual(t1, t2)
            
            
    def test_save_data_1(self):
        entity = self._init_entity(self.data_2)
        entity.add_change(self.data_3)
        
        self.assertSameElements(db_version(entity).data, [])
        entity.save()
        self.assertSameElements(db_version(entity).data, [])
        self.assertTrue(entity.save_data_changes())
        self.assertSameElements(db_version(entity).data, entity.data)
    
    def test_save_data_2(self):
        entity = self._init_entity(self.data_2)
        entity.add_change(self.data_3, replace=True)
        
        entity.reload()
        # 'changes' has the changes, but they have not yet been saved to 'data'
        self.assertSameElements(entity.data, [])
        self.assertEqual(len(entity.changes), 2)
        
        entity.apply_changes(1)
        # save() shouldn't save 'data', 'changes', or 'change_index'
        entity.save()
        entity.reload()
        # Nothing should change
        self.assertSameElements(entity.data, [])
        self.assertEqual(len(entity.changes), 2)
        
        entity.apply_changes(1)
        entity.save_data_changes()
        entity.reload()
        # After calling save_data_changes(), the state of 'data' should be
        # saved to the database
        self.assertSameElements(entity.data, self.data_2)
        self.assertEqual(len(entity.changes), 2)
        
        
    # Testing that two users can modify an entity at the same time without
    # causing rollback issues.
    def test_concurrency_1(self):
        entity = self._init_entity(self.data_2)
        entity.add_change(self.data_3)
        entity.add_change(self.data_4)
        entity.revert_changes(2)
        # Alternate entity. Refers to the same entity in the database as
        # 'entity'
        alt_entity = db_version(entity)
        
        alt_entity.apply_changes()
        self.assertTrue(alt_entity.save_data_changes())
        self.assertSameElements(alt_entity.data, db_version(alt_entity).data)
        del alt_entity
        
        # At this point, 'entity' is out of sync with its database version. The
        # database version has all changes applied, while this version is
        # reverted. When we add something, the database version should become
        # synced with this version.
        entity.add_change(self.data_5)
        self.assertTrue(entity.save_data_changes())
        
        entity._check_invariants_long()
        
        self.assertSameElements(entity.data,
                [{"Transaction_ID":"4444","extra":"asdf"},
                 {"Transaction_ID":"3333","extra":"cat"},])
        self.assertSameElements(db_version(entity).data,
                [{"Transaction_ID":"4444","extra":"asdf"},
                 {"Transaction_ID":"3333","extra":"cat"},])
        
                
        
    # Two users pull from the database, then they both add changes, then they
    # both save. The database data should contain the data from changes by both
    # users.
    def test_concurrency_2(self):
        entity = self._init_entity(self.data_2)

        alt_entity = db_version(entity)

        alt_entity.apply_changes()
        alt_entity.add_change(self.data_1)

        entity.add_change(self.data_4)

        self.assertTrue(entity.save_data_changes())
        self.assertTrue(alt_entity.save_data_changes())
        entity.reload()
        entity.apply_changes()

        entity._check_invariants_long()
        self.assertSameElements(entity.data,
                [{"Transaction_ID":"4444","extra":"asdf"},
                 {"Transaction_ID":"3333","extra":"qwerty"},
                 {"Transaction_ID":"1111","extra":"something"},
                 {"Transaction_ID":"6666","extra":"dog"}])
    
    
    # This test makes sure that saving an entity cannot replace 'entity.changes' in
    # the database with an earlier version
    def test_concurrency_3(self):
        entity = self._init_entity(self.data_2)
        entity.revert_changes()
        entity.add_change(self.data_4)
        
        alt_entity = db_version(entity)
        alt_entity.apply_changes()
        alt_entity.add_change(self.data_1)
        
        # At this point, entity.changes is different from the database version.
        # We will make sure that saving 'entity' does not revert the database
        # version.
        entity.apply_changes()
        self.assertTrue(entity.save_data_changes())
        entity.reload()
        
        entity._check_invariants_long()
        
        alt_entity.reload()
        alt_entity.apply_changes()
        
        self.assertSameElements(alt_entity.data,
                [{"Transaction_ID":"1111","extra":"something"},
                 {"Transaction_ID":"3333","extra":"qwerty"},
                 {"Transaction_ID":"6666","extra":"dog"}])
        
                
    # Tests for the case where:
    # 1. user adds, applies, and saves changes to an entity
    # 2. alternate user pulls same entity from database
    # 3. user reverts and overwrites changes
    # 4. alternate user tries to save
    # 
    # The alternate user should be unable to save.
    def test_concurrency_4(self):
        def printer(entity):
            while True:
                yield str(Entity.objects.get(pk=entity.pk).changes)
        
        # Create an entity with some changes
        entity = self._init_entity(self.data_2)
        entity.add_change(self.data_1)
        entity.save_data_changes()
        
        # Alternate user pulls entity from database, applies all changes locally
        alt_entity = Entity.objects.get(pk=entity.pk)
        
        # Entity reverts and overwrites changes with a new change
        entity.revert_changes()
        entity.add_change(self.data_5)
        success = entity.save_data_changes()
        self.assertTrue(success)
        
        # When the alternate user tries to save, it should fail because its
        # local changes are outdated (from before the most recent revert)
        success = alt_entity.save_data_changes()
        self.assertFalse(success)
        alt_entity._check_invariants_long()
        
        # Partial reload should not fix
        partial_reloads = [["group"], ["data"], ["data","change_index"], ["changes"], ["changes","data"], ["changes","change_index"], ["change_index"]]
        for reload_params in partial_reloads:
            alt_entity.reload(*reload_params)
            alt_entity.apply_changes()
            success = alt_entity.save_data_changes()
            self.assertFalse(success)
        
        
        alt_entity.reload(*reload_params)
        alt_entity.apply_changes()
        success = alt_entity.save_data_changes()
        self.assertFalse(success)
        
        
    # Testing that a user can pull an entity from the database and revert it.
    # def test_concurrency_5(self):
    #     entity = self._init_entity(self.data_2)
    #     entity.add_change(self.data_4, replace=True)
    #     entity.save_data_changes()
    #
    #     alt_entity = db_version(entity)
    #     self.assertSameElements(alt_entity.data, self.data_4)
    #     alt_entity.revert_one()
    #     self.assertSameElements(alt_entity.data, self.data_2)
        
                
    def _init_entity(self, data):
        entity = Entity(**self.default_entity_data)
        entity.save()
        
        entity.add_change(data, replace=True)
        entity.save()
        
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


def db_version(entity):
    return Entity.objects.get(pk=entity.pk)
