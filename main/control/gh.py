# coding: utf-8

from datetime import datetime
import json

import flask
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import urlfetch
import github

import auth
import config
import model
import util
import task

from main import app


@app.route('/<username>')
def gh_account(username):
  username = username.lower()
  account_db = model.Account.get_by_id(username)

  if not account_db:
    g = github.Github(config.CONFIG_DB.github_username, config.CONFIG_DB.github_password)
    try:
      account = g.get_user(username)
    except github.GithubException as error:
      return flask.abort(error.status)

    account_db = model.Account.get_or_insert(
        account.login,
        username=account.login,
        name=account.name or account.login,
        avatar_url=account.avatar_url.split('?')[0],
        organization=account.type == 'Organization',
        public_repos=account.public_repos,
      )

  task.queue_account(account_db)
  repo_dbs, repo_cursor = account_db.get_repo_dbs()

  return flask.render_template(
      'account/view.html',
      html_class='gh-view',
      title=account_db.name,
      account_db=account_db,
      repo_dbs=repo_dbs,
      next_url=util.generate_next_url(repo_cursor),
      username=account_db.username,
    )


@app.route('/admin/top/')
#TODO: Fix the ugliness
def gh_admin_top():
  stars = util.param('stars', int) or 30000
  page = util.param('page', int) or 1
  per_page = util.param('per_page', int) or 16
  result = urlfetch.fetch('https://api.github.com/search/repositories?q=stars:>=%s&sort=stars&page=%d&per_page=%d' % (stars, page, per_page))
  if result.status_code == 200:
    repos = json.loads(result.content)

  for repo in repos['items']:
    account = repo['owner']
    account_db = model.Account.get_or_insert(
        account['login'],
        username=account['login'],
        name=account['login'],
        avatar_url=account['avatar_url'].split('?')[0],
        organization=account['type'] == 'Organization',
      )
  return flask.render_template(
      'admin/popular.html',
      title='Top Repositories',
      next=flask.url_for('gh_admin_top', stars=stars, page=page + 1, per_page=per_page),
      repos=repos,
      stars=stars,
      page=page,
      per_page=per_page,
    )


@app.route('/admin/cron/sync/')
def admin_cron():
  if 'X-Appengine-Cron' not in flask.request.headers:
    flask.abort(403)
  account_dbs, account_cursor = model.Account.get_dbs(
      order=util.param('order') or 'modified',
      status=util.param('status'),
    )

  if util.param('sync', bool):
    for account_db in account_dbs:
      task.queue_account(account_db)
    flask.flash('Trying to sync %s accounts' % len(account_dbs))
  return flask.render_template(
      'account/admin_account_list.html',
      html_class='admin-account-list',
      title='Account List',
      account_dbs=account_dbs,
      next_url=util.generate_next_url(account_cursor),
    )
