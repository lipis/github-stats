# coding: utf-8

import flask

import config
import model
import util

from main import app


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  if util.param('username'):
    return flask.redirect(flask.url_for('gh_account', username=util.param('username')))
  user_dbs, user_cursor = model.Account.get_dbs(
      order='-stars',
      organization=False,
    )

  organization_dbs, organization_cursor = model.Account.get_dbs(
      order='-stars',
      organization=True,
    )

  repo_dbs, repo_cursor = model.Repo.get_dbs(
      order='-stars',
    )

  return flask.render_template(
      'welcome.html',
      html_class='welcome',
      user_dbs=user_dbs,
      organization_dbs=organization_dbs,
      repo_dbs=repo_dbs,
    )


@app.route('/user/')
def user():
  order = util.param('order') or '-stars'
  if 'repo' in order:
    order = '-public_repos'
  elif 'follower' in order:
    order = '-followers'

  user_dbs, user_cursor = model.Account.get_dbs(
      order=order,
      organization=False,
      limit=util.param('limit', int) or config.MAX_DB_LIMIT,
    )
  return flask.render_template(
      'account/list_user.html',
      title='Users',
      html_class='account-user',
      user_dbs=user_dbs,
      order=order,
    )


@app.route('/organization/')
def organization():
  order = util.param('order') or '-stars'
  if 'repo' in order:
    order = '-public_repos'

  organization_dbs, organization_cursor = model.Account.get_dbs(
      order=order,
      organization=True,
      limit=util.param('limit', int) or config.MAX_DB_LIMIT,
    )
  return flask.render_template(
      'account/list_organization.html',
      title='Organizations',
      html_class='account-organization',
      organization_dbs=organization_dbs,
      order=order,
    )


@app.route('/repo/')
def repo():
  order = util.param('order') or '-stars'
  if 'fork' in order:
    order = '-forks'
  repo_dbs, repo_cursor = model.Repo.get_dbs(
      order=order,
      limit=util.param('limit', int) or config.MAX_DB_LIMIT,
    )

  return flask.render_template(
      'account/list_repo.html',
      title='Repositories',
      html_class='account-repo',
      repo_dbs=repo_dbs,
      order=order.replace('-', ''),
    )


###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
      'sitemap.xml',
      lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
    ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
