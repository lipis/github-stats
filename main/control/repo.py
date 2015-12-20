# coding: utf-8

from flask.ext import wtf
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
@app.route('/admin/repo/')
@auth.admin_required
def admin_repo_list():
  repo_dbs, repo_cursor = model.Repo.get_dbs(
      order=util.param('order') or '-modified',
    )
  return flask.render_template(
      'repo/admin_repo_list.html',
      html_class='admin-repo-list',
      title='Repo List',
      repo_dbs=repo_dbs,
      next_url=util.generate_next_url(repo_cursor),
      api_url=flask.url_for('api.admin.repo.list'),
    )


###############################################################################
# Admin Update
###############################################################################
class RepoUpdateAdminForm(wtf.Form):
  name = wtforms.StringField(
      model.Repo.name._verbose_name,
      [wtforms.validators.required()],
      filters=[util.strip_filter],
    )
  description = wtforms.TextAreaField(
      model.Repo.description._verbose_name,
      [wtforms.validators.optional()],
      filters=[util.strip_filter],
    )
  stars = wtforms.IntegerField(
      model.Repo.stars._verbose_name,
      [wtforms.validators.optional()],
    )


@app.route('/admin/repo/create/', methods=['GET', 'POST'])
@app.route('/admin/repo/<int:repo_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_repo_update(repo_id=0):
  if repo_id:
    repo_db = model.Repo.get_by_id(repo_id)
  else:
    repo_db = model.Repo()

  if not repo_db:
    flask.abort(404)

  form = RepoUpdateAdminForm(obj=repo_db)

  account_dbs, account_cursor = model.Account.get_dbs()
  form.account_key.choices = [(c.key.urlsafe(), c.username) for c in account_dbs]
  if flask.request.method == 'GET' and not form.errors:
    form.account_key.data = repo_db.account_key.urlsafe() if repo_db.account_key else None

  if form.validate_on_submit():
    form.account_key.data = ndb.Key(urlsafe=form.account_key.data) if form.account_key.data else None
    form.populate_obj(repo_db)
    repo_db.put()
    return flask.redirect(flask.url_for('admin_repo_list', order='-modified'))

  return flask.render_template(
      'repo/admin_repo_update.html',
      title=repo_db.name if repo_id else 'New Repo',
      html_class='admin-repo-update',
      form=form,
      repo_db=repo_db,
      back_url_for='admin_repo_list',
      api_url=flask.url_for('api.admin.repo', repo_key=repo_db.key.urlsafe() if repo_db.key else ''),
    )
