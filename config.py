import logging
import os
import sys

BACKEND = 'Slack'
CORE_PLUGINS = ('Help','Utils','Health', 'Plugins')

BOT_PREFIX = '.'
MESSAGE_SIZE_LIMIT = 4000

BOT_DATA_DIR = os.getcwd() + '/data'
BOT_EXTRA_PLUGIN_DIR = os.getcwd() + '/plugins'
BOT_EXTRA_STORAGE_PLUGINS_DIR = os.getcwd() + '/storage'

BOT_LOG_FILE = r'./errbot.log'
BOT_LOG_LEVEL = logging.DEBUG

BOT_ADMINS = os.getenv('SLACKPRO_BOT_ADMINS', '').split(',')
BOT_ADMINS_NOTIFICATIONS = BOT_ADMINS

SENTRY_DSN = os.getenv('SLACKPRO_SENTRY_DSN')
SENTRY_LOGLEVEL = BOT_LOG_LEVEL

BOT_ASYNC = True
BOT_ASYNC_POOLSIZE = 16

STORAGE = 'SQL'
STORAGE_CONFIG = {
    'data_url': os.getenv('SLACKPRO_SQL_URL',
                          'postgres://postgres:postgres@postgres/postgres'),
}

BOT_IDENTITY = {
    'token': os.environ['SLACKPRO_SLACK_TOKEN'],
}

if BOT_IDENTITY['token'].startswith('xoxb'):
    print('You need an user token for this to work.')
    print('You can get one from here:')
    print('https://api.slack.com/custom-integrations/legacy-tokens')
    sys.exit(1)
