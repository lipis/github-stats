# coding: utf-8

import github
import flask

import config
import model

from main import app


@app.route('/<username>')
def gh(username):
  username = username.lower()
  account_db = model.Account.get_by_id(username)

  if not account_db:
    g = github.Github()
    try:
      account = g.get_user(username)
    except github.GithubException as error:
      return flask.abort(error.status)

    account_db = model.Account.get_or_insert(
        account.login,
        username=account.login,
        name=account.name,
        avatar_url=account.avatar_url.split('?')[0],
        organization=account.type == 'Organization',
      )

    repos = []
    for project in account.get_repos():
      repos.append(project.name)

  return flask.render_template(
      'account/account_view.html',
      html_class='account-view',
      title=account_db.username,
      account_db=account_db,
    )
