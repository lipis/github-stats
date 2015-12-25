# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Repo(model.Base):
  account_username = ndb.StringProperty(required=True)
  avatar_url = ndb.StringProperty(required=True, verbose_name=u'Avatar URL', indexed=False)
  description = ndb.StringProperty(default='', indexed=False)
  fork = ndb.BooleanProperty(default=False)
  forks = ndb.IntegerProperty(default=0)
  language = ndb.StringProperty(default='')
  name = ndb.StringProperty(required=True)
  stars = ndb.IntegerProperty(default=0)

  @ndb.ComputedProperty
  def stars_hu(self):
    return '{:,}'.format(self.stars)

  @ndb.ComputedProperty
  def forks_hu(self):
    return '{:,}'.format(self.forks)

  @ndb.ComputedProperty
  def url(self):
    return 'https://github.com/%s/%s' % (self.account_username, self.name)

  FIELDS = {
      'account_username': fields.String,
      'avatar_url': fields.String,
      'description': fields.String,
      'forks': fields.Integer,
      'language': fields.String,
      'name': fields.String,
      'stars': fields.Integer,
    }

  FIELDS.update(model.Base.FIELDS)
