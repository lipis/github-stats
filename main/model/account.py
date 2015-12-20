# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Account(model.Base):
  username = ndb.StringProperty(required=True)
  name = ndb.StringProperty(required=True)
  stars = ndb.IntegerProperty(default=0)
  rank = ndb.IntegerProperty(default=0)
  organization = ndb.BooleanProperty(default=False)
  status = ndb.StringProperty(default='new', choices=['new', 'synced', 'syncing', 'error'])
  avatar_url = ndb.StringProperty(required=True, verbose_name=u'Avatar URL')
  public_repos = ndb.IntegerProperty(default=0)

  @ndb.ComputedProperty
  def stars_hu(self):
    return '{:,}'.format(self.stars)

  def get_repo_dbs(self, **kwargs):
    return model.Repo.get_dbs(
        ancestor=self.key,
        order='-stars',
        **kwargs
      )

  FIELDS = {
      'username': fields.String,
      'name': fields.String,
      'stars': fields.Integer,
      'rank': fields.Integer,
      'organization': fields.Boolean,
      'status': fields.String,
      'avatar_url': fields.String,
      'public_repos': fields.Integer,
    }

  FIELDS.update(model.Base.FIELDS)
