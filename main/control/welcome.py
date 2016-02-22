# coding: utf-8

from datetime import datetime
from google.appengine.ext import ndb
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
  person_dbs, person_cursor = model.Account.get_dbs(
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
      title='Top People, Organizations and Repositories',
      person_dbs=person_dbs,
      organization_dbs=organization_dbs,
      repo_dbs=repo_dbs,
    )


@app.route('/new/')
def new_accounts():
  person_dbs, person_cursor = model.Account.get_dbs(
    order='-created',
    limit=128,
  )

  return flask.make_response(flask.render_template(
    'account/list_new.html',
    title='Latest Additions',
    html_class='account-new',
    person_dbs=person_dbs,
  ))


@app.route('/people/')
def person():
  limit = int(util.param('limit', int) or flask.request.cookies.get('limit') or config.MAX_DB_LIMIT)
  order = util.param('order') or '-stars'
  if 'repo' in order:
    order = '-public_repos'
  elif 'follower' in order:
    order = '-followers'

  person_dbs, person_cursor = model.Account.get_dbs(
      order=order,
      organization=False,
      limit=limit,
    )

  response = flask.make_response(flask.render_template(
      'account/list_person.html',
      title='Top People',
      html_class='account-person',
      person_dbs=person_dbs,
      order=order,
      limit=limit,
    ))
  response.set_cookie('limit', str(limit))
  return response


@app.route('/organizations/')
def organization():
  limit = int(util.param('limit', int) or flask.request.cookies.get('limit') or config.MAX_DB_LIMIT)
  order = util.param('order') or '-stars'
  if 'repo' in order:
    order = '-public_repos'

  organization_dbs, organization_cursor = model.Account.get_dbs(
      order=order,
      organization=True,
      limit=limit,
    )

  response = flask.make_response(flask.render_template(
      'account/list_organization.html',
      title='Top Organizations',
      html_class='account-organization',
      organization_dbs=organization_dbs,
      order=order,
      limit=limit,
    ))
  response.set_cookie('limit', str(limit))
  return response


@app.route('/repositories/')
def repo():
  limit = int(util.param('limit', int) or flask.request.cookies.get('limit') or config.MAX_DB_LIMIT)
  order = util.param('order') or '-stars'
  if 'fork' in order:
    order = '-forks'
  repo_dbs, repo_cursor = model.Repo.get_dbs(
      order=order,
      limit=limit,
    )

  response = flask.make_response(flask.render_template(
      'account/list_repo.html',
      title='Top Repositories',
      html_class='account-repo',
      repo_dbs=repo_dbs,
      order=order.replace('-', ''),
      limit=limit,
    ))
  response.set_cookie('limit', str(limit))
  return response


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
