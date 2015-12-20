# coding: utf-8

from datetime import datetime

from google.appengine.ext import ndb
from google.appengine.ext import deferred
import flask
import github

import config
import model
import util

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

  queue_account(account_db)
  repo_dbs, repo_cursor = account_db.get_repo_dbs()

  return flask.render_template(
      'account/view.html',
      html_class='account-view',
      title=account_db.name,
      account_db=account_db,
      repo_dbs=repo_dbs,
      next_url=util.generate_next_url(repo_cursor),
    )


###############################################################################
# Tasks
###############################################################################

def queue_account(account_db):
  if account_db.status in ['new', 'error']:
    account_db.status = 'syncing'
    account_db.put()

  deferred.defer(sync_account, account_db)


def sync_account(account_db):
  g = github.Github(config.CONFIG_DB.github_username, config.CONFIG_DB.github_password)
  try:
    account = g.get_user(account_db.username)
  except github.GithubException as error:
    account_db.status = 'error'

  stars = 0
  repo_dbs = []

  for repo in account.get_repos():
    name = repo.name.lower()
    repo_db = model.Repo.get_or_insert(
        name,
        parent=account_db.key,
        name=repo.name,
        description=repo.description,
        stars=repo.stargazers_count,
        avatar_url=account_db.avatar_url,
        account_username=account_db.username,
      )

    repo_db.name = repo.name
    repo_db.description = repo.description
    repo_db.stars = repo.stargazers_count

    stars += repo_db.stars

  if repo_dbs:
    ndb.put_multi(repo_dbs)

  account_db.name = account.name or account.login
  account_db.status = 'synced'
  account_db.stars = stars
  account_db.put()
