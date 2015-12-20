# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Repo(model.Base):
  name = ndb.StringProperty(required=True)
  description = ndb.StringProperty(default='')
  stars = ndb.IntegerProperty(default=0)
  account_username = ndb.StringProperty(required=True)
  avatar_url = ndb.StringProperty(required=True, verbose_name=u'Avatar URL')

  @ndb.ComputedProperty
  def stars_hu(self):
    return '{:,}'.format(self.stars)

  @ndb.ComputedProperty
  def url(self):
    return 'https://github.com/%s/%s' % (self.account_username, self.name)

  FIELDS = {
      'name': fields.String,
      'description': fields.String,
      'stars': fields.Integer,
      'account_username': fields.String,
      'avatar_url': fields.String,
    }

  FIELDS.update(model.Base.FIELDS)
