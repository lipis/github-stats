# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask_restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/account/', endpoint='api.account.list')
class AccountListAPI(flask_restful.Resource):
  def get(self):
    account_dbs, account_cursor = model.Account.get_dbs()
    return helpers.make_response(account_dbs, model.Account.FIELDS, account_cursor)


@api_v1.resource('/account/<string:account_key>/', endpoint='api.account')
class AccountAPI(flask_restful.Resource):
  def get(self, account_key):
    account_db = ndb.Key(urlsafe=account_key).get()
    if not account_db:
      helpers.make_not_found_exception('Account %s not found' % account_key)
    return helpers.make_response(account_db, model.Account.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/account/', endpoint='api.admin.account.list')
class AdminAccountListAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self):
    account_keys = util.param('account_keys', list)
    if account_keys:
      account_db_keys = [ndb.Key(urlsafe=k) for k in account_keys]
      account_dbs = ndb.get_multi(account_db_keys)
      return helpers.make_response(account_dbs, model.account.FIELDS)

    account_dbs, account_cursor = model.Account.get_dbs()
    return helpers.make_response(account_dbs, model.Account.FIELDS, account_cursor)


@api_v1.resource('/admin/account/<string:account_key>/', endpoint='api.admin.account')
class AdminAccountAPI(flask_restful.Resource):
  @auth.admin_required
  def get(self, account_key):
    account_db = ndb.Key(urlsafe=account_key).get()
    if not account_db:
      helpers.make_not_found_exception('Account %s not found' % account_key)
    return helpers.make_response(account_db, model.Account.FIELDS)
