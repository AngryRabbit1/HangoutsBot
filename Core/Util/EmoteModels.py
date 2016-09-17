# -*- coding: utf-8 -*-

import logging
from peewee import Model, IntegerField, CharField, BigIntegerField
from .UtilBot import db


log = logging.getLogger(__name__)


class BaseModel(Model):
	class Meta:
		database = db


class Ascii_Emotes(BaseModel):
	emote_pk = IntegerField(primary_key=True)
	user_id = BigIntegerField()
	emote_name = CharField(max_length=20)
	emote_string = CharField(max_length=255)

	class Meta:
		indexes = ((('user_id', 'emote_name'), True),)