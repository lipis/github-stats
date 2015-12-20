# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/repo/', endpoint='api.repo.list')
class RepoListAPI(restful.Resource):
  def get(self):
    repo_dbs, repo_cursor = model.Repo.get_dbs()
    return helpers.make_response(repo_dbs, model.Repo.FIELDS, repo_cursor)


@api_v1.resource('/repo/<string:repo_key>/', endpoint='api.repo')
class RepoAPI(restful.Resource):
  def get(self, repo_key):
    repo_db = ndb.Key(urlsafe=repo_key).get()
    if not repo_db:
      helpers.make_not_found_exception('Repo %s not found' % repo_key)
    return helpers.make_response(repo_db, model.Repo.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/repo/', endpoint='api.admin.repo.list')
class AdminRepoListAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    repo_keys = util.param('repo_keys', list)
    if repo_keys:
      repo_db_keys = [ndb.Key(urlsafe=k) for k in repo_keys]
      repo_dbs = ndb.get_multi(repo_db_keys)
      return helpers.make_response(repo_dbs, model.repo.FIELDS)

    repo_dbs, repo_cursor = model.Repo.get_dbs()
    return helpers.make_response(repo_dbs, model.Repo.FIELDS, repo_cursor)


@api_v1.resource('/admin/repo/<string:repo_key>/', endpoint='api.admin.repo')
class AdminRepoAPI(restful.Resource):
  @auth.admin_required
  def get(self, repo_key):
    repo_db = ndb.Key(urlsafe=repo_key).get()
    if not repo_db:
      helpers.make_not_found_exception('Repo %s not found' % repo_key)
    return helpers.make_response(repo_db, model.Repo.FIELDS)
