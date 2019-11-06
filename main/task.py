# coding: utf-8

import operator
from datetime import datetime
from datetime import timedelta
import logging

from google.appengine.api import mail
from google.appengine.ext import deferred
from google.appengine.ext import ndb
import flask
import github

import config
import util
import model


###############################################################################
# Helpers
###############################################################################
def send_mail_notification(subject, body, to=None, **kwargs):
  if not config.CONFIG_DB.feedback_email:
    return
  brand_name = config.CONFIG_DB.brand_name
  sender = '%s <%s>' % (brand_name, config.CONFIG_DB.feedback_email)
  subject = '[%s] %s' % (brand_name, subject)
  if config.DEVELOPMENT:
    logging.info(
      '\n'
      '######### Deferring sending this email: #############################'
      '\nFrom: %s\nTo: %s\nSubject: %s\n\n%s\n'
      '#####################################################################',
      sender, to or sender, subject, body
    )
  deferred.defer(mail.send_mail, sender, to or sender, subject, body, **kwargs)


###############################################################################
# Admin Notifications
###############################################################################
def new_user_notification(user_db):
  if not config.CONFIG_DB.notify_on_new_user:
    return
  body = 'name: %s\nusername: %s\nemail: %s\n%s\n%s' % (
    user_db.name,
    user_db.username,
    user_db.email,
    ''.join([': '.join(('%s\n' % a).split('_')) for a in user_db.auth_ids]),
    flask.url_for('user_update', user_id=user_db.key.id(), _external=True),
  )

  if user_db.github:
    body += '\n\n%s' % (flask.url_for('gh_account', username=user_db.github, _external=True))
  send_mail_notification('New user: %s' % user_db.name, body)


###############################################################################
# User Related
###############################################################################
def verify_email_notification(user_db):
  if not (config.CONFIG_DB.verify_email and user_db.email) or user_db.verified:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = '%s <%s>' % (user_db.name, user_db.email)
  body = '''Hello %(name)s,

It seems someone (hopefully you) tried to verify your email with %(brand)s.

If it was you, please verify it by following this link:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'name': user_db.name,
    'link': flask.url_for('user_verify', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'A verification link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Verify your email.', body, to)


def reset_password_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = '%s <%s>' % (user_db.name, user_db.email)
  body = '''Hello %(name)s,

It seems someone (hopefully you) tried to reset your password with %(brand)s.

If it was you, please reset it by following this link:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'name': user_db.name,
    'link': flask.url_for('user_reset', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'A reset link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Reset your password', body, to)


def activate_user_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = user_db.email
  body = '''Welcome to %(brand)s.

Follow the link below to confirm your email address and activate your account:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
    'link': flask.url_for('user_activate', token=user_db.token, _external=True),
    'brand': config.CONFIG_DB.brand_name,
  }

  flask.flash(
    'An activation link has been sent to your email address.',
    category='success',
  )
  send_mail_notification('Activate your account', body, to)


###############################################################################
# Admin Related
###############################################################################
def email_conflict_notification(email):
  body = 'There is a conflict with %s\n\n%s' % (
    email,
    flask.url_for('user_list', email=email, _external=True),
  )
  send_mail_notification('Conflict with: %s' % email, body)


###############################################################################
# GH Tasks
###############################################################################
def queue_account(account_db):
  import logging
  if account_db.status in ['404']:
    return

  max_repos = 3000
  queue_it = False
  delta = datetime.utcnow() - account_db.synced

  if account_db.status in ['new', 'error']:
    account_db.status = 'syncing'
    account_db.synced = datetime.utcnow()
    account_db.put()
    queue_it = True

  elif delta.days > 0 and account_db.status == 'failed' and account_db.public_repos < max_repos:
    account_db.status = 'syncing'
    account_db.synced = datetime.utcnow()
    account_db.put()
    queue_it = True

  elif account_db.status == 'syncing':
    if delta.seconds > 60 * 60 or account_db.public_repos > max_repos:
      account_db.status = 'failed'
      account_db.synced = datetime.utcnow()
      account_db.put()
    elif delta.seconds > 30 * 60:
      queue_it = True

  # older than 4 hours long sunc them
  if (delta.days > 0 or delta.seconds > 60 * 60 * 4) and account_db.status != 'failed':
    account_db.status = 'syncing'
    account_db.synced = datetime.utcnow()
    account_db.put()
    queue_it = True

  if queue_it:
    deferred.defer(sync_account, account_db)


def sync_account(account_db):
  g = github.Github(config.CONFIG_DB.github_username, config.CONFIG_DB.github_password)
  try:
    account = g.get_user(account_db.username)
  except github.GithubException as error:
    account_db.status = 'error'
    if error.status in [404]:
      account_db.status = str(error.status)
    account_db.put()
    return

  account_db.name = account.name or account.login
  account_db.followers = account.followers
  account_db.email = account.email or ''
  account_db.public_repos = account.public_repos
  account_db.joined = account.created_at
  account_db.organization = account.type == 'Organization'
  account_db.avatar_url = account.avatar_url.split('?')[0]
  account_db.put()

  stars = 0
  forks = 0
  repo_dbs = []
  languages = {}

  for repo in account.get_repos():
    name = repo.name.lower()
    if name in config.ILLEGAL_KEYS:
      name = 'gh-%s' % name
    repo_db = model.Repo.get_or_insert(
        name,
        parent=account_db.key,
        name=repo.name,
        description=repo.description[:500] if repo.description else '',
        stars=repo.stargazers_count,
        fork=repo.fork,
        forks=repo.forks_count,
        language=repo.language or '',
        avatar_url=account_db.avatar_url,
        account_username=account_db.username,
      )

    repo_db.description = repo.description[:500] if repo.description else ''
    repo_db.fork = repo.fork
    repo_db.forks = repo.forks_count
    repo_db.language = repo.language or ''
    repo_db.name = repo.name
    repo_db.stars = repo.stargazers_count

    stars += repo_db.stars
    forks += repo_db.forks
    repo_dbs.append(repo_db)

    if repo_db.language and not repo_db.fork:
      if repo_db.language not in languages:
        languages[repo_db.language] = repo_db.stars + 1
      else:
        languages[repo_db.language] += repo_db.stars + 1

  if repo_dbs:
    ndb.put_multi_async(repo_dbs)

  account_db.language = max(languages.iteritems(), key=operator.itemgetter(1))[0] if languages else ''
  account_db.status = 'synced'
  account_db.synced = datetime.utcnow()
  account_db.stars = stars
  account_db.forks = forks
  account_db.put()


###############################################################################
# Repo Clean-ups
###############################################################################
def queue_repo_cleanup(days=3):
  deferred.defer(repo_cleanup, days)


def repo_cleanup(days, cursor=None):
  before_date = datetime.utcnow() - timedelta(days=days)
  repo_qry = model.Repo.query().filter(model.Repo.modified < before_date)
  repo_keys, repo_cursors = util.get_dbs(
      repo_qry,
      order='modified',
      keys_only=True,
      cursor=cursor,
    )

  ndb.delete_multi(repo_keys)
  if repo_cursors['next']:
    deferred.defer(repo_cleanup, days, repo_cursors['next'])


###############################################################################
# Account Clean-ups
###############################################################################
def queue_account_cleanup(stars=10000):
  deferred.defer(account_cleanup, stars)


def account_cleanup(stars, cursor=None):
  account_qry = model.Account.query().filter(model.Account.stars < stars)
  account_keys, account_cursors = util.get_dbs(
      account_qry,
      order='stars',
      keys_only=True,
      cursor=cursor,
    )

  ndb.delete_multi(account_keys)
  if account_cursors['next']:
    deferred.defer(account_cleanup, days, account_cursors['next'])


###############################################################################
# Rank Accounts
###############################################################################
def rank_accounts(stars=10000):
  deferred.defer(account_rank, True)
  deferred.defer(account_rank, False)


def account_rank(organization):
  account_qry = model.Account.query().filter(model.Account.organization == organization)
  account_dbs, account_cursors = util.get_dbs(
    account_qry,
    order='-stars',
    limit=-1,
  )
  updated_dbs = []
  for index, account_db in enumerate(account_dbs, start=1):
    if index < config.MAX_DB_LIMIT:
      account_db.rank = index
    else:
      account_db.rank = 0
    updated_dbs.append(account_db)

  ndb.put_multi(updated_dbs)
