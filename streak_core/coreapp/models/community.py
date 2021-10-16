from mongoengine import *
import datetime
from django.utils import timezone


class Interaction(Document):
	interaction_uuid = StringField(max_length=100,required=True)
	user_uuid = StringField(max_length=100,required=True)
	interaction_type = StringField(max_length=50) #view/subscribe/share/vote/downvote/comment/report/flag etc
	owner_uuid = StringField(max_length=100,required=True) # publishing uuid, backtest shared uuid, other interaction uuid etc
	element_uuid = StringField(max_length=100,required=True) # publishing uuid, backtest shared uuid, other interaction uuid etc
	element_type = StringField(max_length=50,required=True) # publsihed algo, share backtest, video,comment etc
	interaction_subtype = StringField() # upvote/downvote
	interaction_value = StringField() # 0,1,-1
	interaction_imgurl = StringField() # if and gif, or image is posted as reponse 

	interaction_action = StringField() # upvote
	created_at = DateTimeField()
	updated_at = DateTimeField(default=datetime.datetime.now)
	meta = {
    'indexes': [
        {'fields': ('user_uuid','interaction_uuid','element_uuid','owner_uuid','user_uuid')}
    	]
	}
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(Interaction, self).save(*args, **kwargs)

# class RatingInteraction(Document):
# 	user_uuid = StringField(max_length=100,required=True)
# 	element_uuid = StringField(max_length=100,required=True)
# 	element_type = StringField(max_length=50,required=True)
# 	interaction_value = IntField() # 0,1,-1
# 	created_at = DateTimeField()
# 	updated_at = DateTimeField(default=datetime.datetime.now)
# 	meta = {
#     'indexes': [
#         {'fields': ('user_uuid','element_uuid')}    	]
# 	}
# 	def save(self, *args, **kwargs):
# 		if not self.created_at:
# 			self.created_at = datetime.datetime.now()
# 		self.updated_at = datetime.datetime.now()
# 		return super(RatingInteraction, self).save(*args, **kwargs)