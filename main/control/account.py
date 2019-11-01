# coding: utf-8

import flask_wtf
from google.appengine.ext import ndb
import flask
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/account/')
@auth.admin_required
def admin_account_list():
  account_dbs, account_cursor = model.Account.get_dbs(
      order=util.param('order') or '-modified',
    )
  return flask.render_template(
      'account/admin_account_list.html',
      html_class='admin-account-list',
      title='Account List',
      account_dbs=account_dbs,
      next_url=util.generate_next_url(account_cursor),
      api_url=flask.url_for('api.admin.account.list'),
    )


###############################################################################
# Admin Update
###############################################################################
class AccountUpdateAdminForm(flask_wtf.Form):
  username = wtforms.StringField(
      model.Account.username._verbose_name,
      [wtforms.validators.required()],
      filters=[util.strip_filter],
    )
  name = wtforms.StringField(
      model.Account.name._verbose_name,
      [wtforms.validators.required()],
      filters=[util.strip_filter],
    )
  stars = wtforms.IntegerField(
      model.Account.stars._verbose_name,
      [wtforms.validators.optional()],
    )
  rank = wtforms.IntegerField(
      model.Account.rank._verbose_name,
      [wtforms.validators.optional()],
    )
  organization = wtforms.BooleanField(
      model.Account.organization._verbose_name,
      [wtforms.validators.optional()],
    )
  status = wtforms.StringField(
      model.Account.status._verbose_name,
      [wtforms.validators.optional()],
      filters=[util.strip_filter],
    )


@app.route('/admin/account/create/', methods=['GET', 'POST'])
@app.route('/admin/account/<int:account_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_account_update(account_id=0):
  if account_id:
    account_db = model.Account.get_by_id(account_id)
  else:
    account_db = model.Account()

  if not account_db:
    flask.abort(404)

  form = AccountUpdateAdminForm(obj=account_db)

  if form.validate_on_submit():
    form.populate_obj(account_db)
    account_db.put()
    return flask.redirect(flask.url_for('admin_account_list', order='-modified'))

  return flask.render_template(
      'account/admin_account_update.html',
      title=account_db.username if account_id else 'New Account',
      html_class='admin-account-update',
      form=form,
      account_db=account_db,
      back_url_for='admin_account_list',
      api_url=flask.url_for('api.admin.account', account_key=account_db.key.urlsafe() if account_db.key else ''),
    )
