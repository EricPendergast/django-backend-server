# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import *
from django.contrib.auth.hashers import check_password, make_password
from .users import Group
import project.settings

import datetime
import sys
import eledata.util

# Create your models here.

# example entity document


class DataHeader(EmbeddedDocument):
    source = StringField()
    mapped = StringField()
    data_type = StringField()


class DataSummary(EmbeddedDocument):
    key = StringField()
    value = StringField()
    order = IntField(unique=True)

class File(EmbeddedDocument):
    filename = StringField()
    is_header_included = BooleanField()

class DataSource(EmbeddedDocument):
    file = EmbeddedDocumentField(File)
    link = StringField()
    account = StringField()
    password = StringField(max_length=255)

    def check_password(self, raw_password):
        """
        Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        """
        Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        self.password = make_password(raw_password)
        self.save()
        return self
    
class Change(Document):
    # The final state of all changed or added rows
    new_rows = ListField()
    # TODO: I think old_rows is re-populated each time. This could be fixed by making Change be a non-embedded document, or by jumping throug some hoops with saving.
    # The original state of all rows that were changed or removed by calling the enact() method
    old_rows = ListField()
    # 'enact' says whether the enact() method has been called on this object.
    # This is used to determine whether to populate 'old_rows' with the rows
    # that were changed/removed when calling the enact() method.
    enacted = BooleanField(required=True, default=False)
    
    remove_all = BooleanField(required=True)
    
    def enact(self, entity):
        if not self.enacted and self.remove_all:
            self.old_rows = list(entity.data)
        # 1. Remove old_rows from data
        # 2. Add new_rows to data
        
        removed_rows = self._add_remove_rows(
                add=self.new_rows,
                remove=self.old_rows,
                entity=entity,
                return_replaced_rows=not self.enacted)
        
        if not self.enacted:
            # Note the use of extend() and not +=. This is because of a (most
            # likely) bug in mongoengine where using += does not tell the
            # model that the field has been updated.
            self.old_rows.extend(removed_rows)
            
            self.enacted = True
            self.save()
            
        
    def revert(self, entity):
        assert self.enacted
        # 1. Remove new_rows from data
        # 2. Add old_rows to data
        self._add_remove_rows(
                add=self.old_rows,
                remove=self.new_rows,
                entity=entity)
        
    
    def _add_remove_rows(self, add, remove, entity, return_replaced_rows=False):
        replaced_rows = []
        id_field = project.settings.CONSTANTS['entity']['header_id_field'][entity.type]
        
        # Maps the transaction id of each transaction to the transaction data
        data_dict = {}
        for row in entity.data:
            row_id = row[id_field]
            data_dict[row_id] = row
        
        # Removing all the old rows
        if remove is not None:
            for row in remove:
                row_id = row[id_field]
                del data_dict[row_id]
            
        # Adding all the new rows, saving the replaced rows 
        for row in add:
            row_id = row[id_field]
            if return_replaced_rows and row_id in data_dict:
                replaced_rows += [data_dict[row_id],]
            data_dict[row_id] = row
        
        entity.data = list(data_dict.values())
        
        return replaced_rows
        
    
    def __str__(self):
        return "(new_rows: " + str(self.new_rows) + ", old_rows: " + (str(self.old_rows) if self.enacted else "Not generated") + ")"



class Entity(Document):
    '''
    Holds arbitrary data, as well as its change history. Each entity is
    associated with a group, represented by its 'group' field.
    
    Some notes about editing data:
    - 'data' should never be modified directly. It should only be modified
      through applying/reverting changes. Modifying 'data' directly will mean
      rollbacks will have incorrect behavior, and _check_invariants_long() will
      fail.
    
    - Changes made to 'data' are not saved through the standard save() method.
      In order to save these, you must call save_data_changes(). It is done
      this way because data changes need to be saved in a way that prevents
      race conditions.
    '''
    
    state = IntField()
    type = StringField(max_length=20)
    source_type = StringField(max_length=15)
    source = EmbeddedDocumentField(DataSource)
    data_summary = EmbeddedDocumentListField(DataSummary)
    data_summary_chart = EmbeddedDocumentListField(DataSummary)
    # Maybe TODO: make this a dict field
    data = ListField()
    data_header = EmbeddedDocumentListField(DataHeader)
    allowed_user = ListField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    group = ReferenceField(Group)
    
    # Here is an explanation of the control flow of adding changes to and rolling
    # back 'data':
    #
    # The only ways the user can change data is by adding a list of rows
    # (replacing any rows that share a row id with a row in the given list),
    # choosing whether to remove all previous data, or not to.
    #
    # Every change to 'data' is expressed through a Change object in 'changes'.
    # Each change object contains a list of rows to remove, and a list of rows to
    # add. This design makes Change objects easy to reverse. One added
    # complication is that the list of rows to remove isn't populated until the
    # first time the change object is enacted. This is to fix race conditions;
    # Since a change could be applied and saved from anywhere at the same time,
    # there is no way of knowing that the local 'data' is the same as what is in
    # the database.
    #
    # There is an array of Change objects, 'changes', which contains all changes
    # users have created, in the order they should be enacted. The current state
    # of 'data' is the result of applying, in order, changes[0] to
    # changes[change_index] to an empty list.
    #
    # Since each change is reversible, a rollback can be performed by undoing
    # each change one by one.
    
    change_index = IntField(default=-1)
    # TODO: make it so that 'changes' isn't retrieved all at once
    # TODO: may need to make changes be an array of references
    # See EntityRollbackTestCase.test_concurrency_5()
    changes = ListField(ReferenceField(Change))
    
    def __init__(self, *args, **kwargs):
        # Contains the most recent time this entities changes were synched with
        # the database. This is used to determine if the user can save changes
        # in save_data_changes().
        # self.time_last_changes_sync is not a database field; it is being
        # initialized here.
        self.time_last_changes_sync = 0
        self.on_changes_sync()
        return super(Entity, self).__init__(*args, **kwargs)
    
    # Contains the most recent time the user reverted changes and then added
    # changes. This can be thought of as keeping track of the most recent time
    # 'changes' was changed in a way besides pushing to the end.
    time_last_revert_overwrite = FloatField(default=0)
    
    # To be called whenever this users changes are synced with the database
    def on_changes_sync(self):
        self.time_last_changes_sync = eledata.util.get_time()
    
        
    # Applies changes 'num_changes' times, stopping once no more changes can be
    # applied. If called with no arguments, reverts all changes.
    def revert_changes(self, num_changes=float('inf')):
        while num_changes > 0 and self.revert_one():
            num_changes -= 1
            
            
    # Returns False if there are no more changes to be reverted, otherwise,
    # reverts one change and returns true
    def revert_one(self):
        assert self.change_index < len(self.changes)
        if self.change_index < 0:
            return False
        self.changes[self.change_index].revert(self)
        self.change_index -= 1
        
        return True
    
    
    # Applies changes 'num_changes' times, stopping once no more changes can be
    # applied. If called with no arguments, applies all changes.
    def apply_changes(self, num_changes=float('inf')):
        while num_changes > 0 and self.apply_one():
            num_changes -= 1
            
        
    # Returns False if there are no more changes to be applied, otherwise,
    # applies one change and returns true
    def apply_one(self):
        if self.change_index+1 >= len(self.changes):
            return False
        
        self.change_index += 1
        self.changes[self.change_index].enact(self)
        
        return True
        
    
    def reload(self, *fields, **kwargs):
        if not fields or set(self.do_not_save).issubset(fields):
            self.on_changes_sync()
            
        return super(Entity, self).reload(*fields, **kwargs)
            
    
    # A way to modify 'changes', avoiding race conditions.
    def add_change(self, data, replace=False):
        self._check_invariants()
        change = Change()
        change.new_rows = data
        # Because of concurrency issues, we don't yet know what data we will be
        # replacing, so old_rows is empty for now. It will be filled when
        # change.enact() is called.
        change.old_rows = []
        change.remove_all = replace
        change.save()
    
        if self.change_index < len(self.changes)-1:
            self.changes = self.changes[:self.change_index+1] + [change,]
            
            # Must save everything (as opposed to just self.changes) to ensure
            # that self.changes, self.change_index, and self.data are all in
            # sync. For example, if someone called apply_changes() during this
            # method, self.change_index could point to an index outside the
            # range of self.changes, which violates an invariant of this class.
            # See EntityRollbackTestCase.test_concurrency_1()
            Entity.objects(pk=self.pk).update(changes=self.changes, data=self.data, change_index=self.change_index, time_last_revert_overwrite=eledata.util.get_time())
        else:
            # Must push to database to ensure no changes made by other users
            # are overwritten.
            Entity.objects(pk=self.pk).update(push__changes=change)
            
        # This line is here because this method does not update 'changes',
        # 'data', or 'change_index' locally.
        self.reload()
        self.apply_changes()
        
        self._check_invariants()
        
        
    # Since 'changes', 'change_index', and 'data' must be in sync according to
    # _check_invariants_long() saving only one or two of them (as opposed to
    # all three) could lead to invariants being false. This is why the save
    # method does not save these three fields. There is a special method that
    # saves all three of these fields at once, save_data_changes()
    do_not_save = ['changes','change_index', 'data']
    def save(self, *args, **kwargs):
        # HACK: We are probably not supposed to modify _changed_fields
        # directly, but there is no other way I've found to exclude a field
        # from saving.
        # Removing each field in self.do_not_save from self._changed_fields. This
        # has the effect of not saving these fields when we call super.save()
        if hasattr(self, '_changed_fields'):
            for to_remove in self.do_not_save:
                assert hasattr(self, to_remove)
                if to_remove in self._changed_fields:
                    self._changed_fields.remove(to_remove)

        super(Entity, self).save(*args, **kwargs)

    
    # Saves the data and change_index of this entity, failing if the database
    # entity has been reverted since the last database sync.
    def save_data_changes(self):
        # This will only exist if the time of the last db sync is more recent
        # than the time of the last revert.
        db_entity = Entity.objects(
                pk=self.pk, 
                time_last_revert_overwrite__lt=self.time_last_changes_sync)
        # If 'db_entity' doesn't exist, this line  won't update anything, and
        # 'ret' will contain an error code.
        ret = db_entity.update(change_index=self.change_index, data=self.data)
        
        
        return ret != 0
        
    
    def _check_invariants(self):
        assert self.change_index >= -1
        assert self.change_index < len(self.changes)
    
    # Only run for tests; this function does a lot of processing
    def _check_invariants_long(self):
        self._check_invariants()
        
        # Enacting changes[0] to changes[change_index] on a dummy object and
        # seeing if its data is the same as the data of this object.
        dummy = Entity()
        dummy.data = []
        dummy.type = self.type
        for i in range(self.change_index+1):
            # assert self.changes[i].enacted
            self.changes[i].enact(dummy)
        
        for item in self.data:
            assert item in dummy.data
        for item in dummy.data:
            assert item in self.data
