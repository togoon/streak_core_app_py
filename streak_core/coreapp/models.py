from __future__ import unicode_literals

from django.db import models
from mongoengine import *
import datetime
from django.utils import timezone
# Create your models here.

class UserProfile(Document):
	"""mongo document to store users data profile"""
	# def __init__(self, arg):
	# 	super(UserProfile, self).__init__()
	# 	self.arg = arg
	uuid = StringField(max_length=500, required=True)
	first_name = StringField(max_length=50, required=True)
	last_name = StringField(max_length=50, required=True)

	phone_regex = r'^\+?1?\d{9,15}$'

	phone_number = StringField(regex=phone_regex,max_length=15, required=True)
	email = StringField(max_length=50, required=True,unique=True)
	email2 = StringField(max_length=50, required=True,default='')
	password = StringField(max_length=100,required=True)
	status = IntField(default=0)
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	# probably add some browser identifier cookie to be able to avoid multi-account issues

	def __unicode__(self):
		return self.email

	def check_password(self, raw_password):
		import hashlib
		# ... get 'hsh_passwd' from database based on 'user' ...
		hsh_passwd = self.password
		# hsh_passwd = hsh_passwd.split('$')
		salt = ''#hsh_passwd[1]
		# print hsh_passwd
		print hashlib.sha1(raw_password).hexdigest()
		if hsh_passwd == hashlib.sha1(raw_password).hexdigest():
			return True
		return False

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserProfile, self).save(*args, **kwargs)
		
class UserVerification(Document):
	"""docstring for UserVerification"""
	uuid = StringField(max_length=500, required=True)
	activation_key = StringField(max_length=40, blank=True)
	otp_key = StringField(max_length=4, blank=True)
	used = BooleanField(default=False)
	key_expires = DateTimeField(default=timezone.now)

	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)

	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(UserVerification, self).save(*args, **kwargs)