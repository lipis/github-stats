# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Account(model.Base):
  avatar_url = ndb.StringProperty(required=True, verbose_name=u'Avatar URL', indexed=False)
  email = ndb.StringProperty(default='')
  followers = ndb.IntegerProperty(default=0)
  forks = ndb.IntegerProperty(default=0)
  joined = ndb.DateTimeProperty()
  synced = ndb.DateTimeProperty(auto_now_add=True)
  name = ndb.StringProperty(required=True)
  organization = ndb.BooleanProperty(default=False)
  public_repos = ndb.IntegerProperty(default=0)
  rank = ndb.IntegerProperty(default=0)
  stars = ndb.IntegerProperty(default=0)
  status = ndb.StringProperty(default='new', choices=['new', 'synced', 'syncing', 'error', 'failed', '404'])
  username = ndb.StringProperty(required=True)
  language = ndb.StringProperty()

  @ndb.ComputedProperty
  def stars_hu(self):
    return '{:,}'.format(self.stars)

  @ndb.ComputedProperty
  def forks_hu(self):
    return '{:,}'.format(self.forks)

  @ndb.ComputedProperty
  def followers_hu(self):
    return '{:,}'.format(self.followers)

  @ndb.ComputedProperty
  def public_repos_hu(self):
    return '{:,}'.format(self.public_repos)

  def get_repo_dbs(self, **kwargs):
    return model.Repo.get_dbs(
        ancestor=self.key,
        order='-stars',
        **kwargs
      )

  FIELDS = {
      'avatar_url': fields.String,
      'email': fields.String,
      'followers': fields.Integer,
      'forks': fields.Integer,
      'joined': fields.DateTime,
      'synced': fields.DateTime,
      'name': fields.String,
      'organization': fields.Boolean,
      'public_repos': fields.Integer,
      'rank': fields.Integer,
      'stars': fields.Integer,
      'status': fields.String,
      'username': fields.String,
    }

  FIELDS.update(model.Base.FIELDS)
