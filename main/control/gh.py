# coding: utf-8

import github
import flask

import config

from main import app


@app.route('/gh/<username>')
def gh(username):
  g = github.Github()
  try:
    account = g.get_user(username)
  except github.GithubException as error:
    return flask.abort(error.status)

  repos = []
  for project in account.get_repos():
    repos.append(project.name)

  return '%r' % ' '.join(repos)
