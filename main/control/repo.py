# coding: utf-8

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
