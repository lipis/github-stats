# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Repo(model.Base):
  name = ndb.StringProperty(required=True)
  description = ndb.StringProperty(default='')
  stars = ndb.IntegerProperty(default=0)

  FIELDS = {
      'name': fields.String,
      'description': fields.String,
      'stars': fields.Integer,
      'account_key': fields.Key,
    }

  FIELDS.update(model.Base.FIELDS)
