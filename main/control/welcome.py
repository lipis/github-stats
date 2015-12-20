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
  user_dbs, user_cursor = model.Account.get_dbs(
      order='-stars',
      limit=16,
      organization=False,
    )

  organization_dbs, organization_cursor = model.Account.get_dbs(
      order='-stars',
      limit=16,
      organization=True,
    )

  repo_dbs, repo_cursor = model.Repo.get_dbs(
      order='-stars',
      limit=16,
    )

  return flask.render_template(
      'welcome.html',
      html_class='welcome',
      user_dbs=user_dbs,
      organization_dbs=organization_dbs,
      repo_dbs=repo_dbs,
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
