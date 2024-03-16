from django.db import models
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import delete_history
from collections import deque


class SDStructure:
    def __init__(self,obj):
        authentication_model = settings.MY_AUTHENTICATION_MODEL
        if isinstance(obj,authentication_model):
            raise Exception("the user parameter in delete() should be an instance of {} but it is {}".format(authentication_model,obj))
        self.deleted_at = timezone.now()   
        self.deleted_by = self.obj
        self.restored_by = None
        self.restored_at = None
    
    
    
    
    def __str__(self):
        return str(self.deleted_at)
    
    


class SoftDeleteManager(models.Manager):
    
    def get_queryset(self,deleted=False):
        return super().get_queryset().filter(is_deleted = deleted)
    
    
    def all(self, deleted=False):
        if deleted == True:
            return self.get_queryset(deleted).order_by('-deleted_at')
        return self.get_queryset(deleted)
        
        


class Model(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.ForeignObject(settings.MY_AUTHENTICATION_MODEL, on_delete=models.SET_NULL, null=True)
    history = delete_history.DequeField()
 
    objects = SoftDeleteManager()
    
    class Meta:
        abstract = True
        
    def delete(self,user=None):
        authentication_model = settings.MY_AUTHENTICATION_MODEL
        """ this method won't delete rather it will set is_deleted feild to True"""
        if not (user and  isinstance(user,authentication_model)):
            raise Exception("the user parameter in delete() should be an instance of {} but it is {}".format(authentication_model,user))
        
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        
        history_obj = SDStructure(user)
        journal_entry = self.journals()
        journal_entry.appendleft(history_obj)
        self.save()
        
    def hard_delete(self):
        """this is the actual delete method of django 
        """
        super(Model,self).delete()
        
    
    def restore(self,user):
        """ this method will restore the deleted object """
        
        authentication_model = settings.MY_AUTHENTICATION_MODEL
        if not (user and  isinstance(user,authentication_model)):
            raise Exception("the user parameter in delete() should be an instance of {} but it is {}".format(authentication_model,user))
        
        self.is_deleted = False
        self.deleted_at = None
        journal_entry = self.journals()
        obj = journal_entry[0]
        obj.restored_by = user
        obj.restored_at = timezone.now()
        self.save()
        
        
        
    def journals(self):
        """ this will create a dequeue class"""
        if isinstance(self.history, deque):
            return self.history
        else:
            return deque()
    