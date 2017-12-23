import logging
import datetime
from errbot import BotPlugin, botcmd

log = logging.getLogger('errbot.gutils')

class Gutils(BotPlugin):
    """Groups utils"""

    def activate(self):
        super().activate()

        # Init incr key
        try:
            _ = self['audit_incr']
        except:
            self['audit_incr'] = 0

        # Initialize DB
        for i in ('groups', 'users'):
            try:
                _ = self[i]
            except KeyError:
                self[i] = {}

        # Initialize Gcoldstorage
        self.store = self.get_plugin('gcoldstorage').store

    def audit(self, frm, event, group, target=None, extras={}):
        '''Log a Groups event'''

        ## Get next incr ID
        next_id = self['audit_incr'] + 1
        self['audit_incr'] = next_id

        ## Write to that ID
        blob = {
            'time': datetime.datetime.now().isoformat(),
            'from': frm,
            'event': event,
            'group': group,
            'target': target,
            'extras': extras,
        }
        self.store(f'audit_event_{next_id}', blob)
        log.debug(blob)

    def read_key(self, key):
        return self[key]

    def _can_add_to_group(self, userid, group):
        if userid in self.bot_config.BOT_ADMINS:
            return True

        return self.is_user_in_group(userid, group)

    def _get_user_group(self, userid, group):
        try:
            return self[f'user:{userid}:{group}']
        except (KeyError, IndexError):
            return None

    def is_user_in_group(self, userid, group):
        return bool(self._get_user_group(userid, group))

    def get_groups_of_user(self, userid):
        try:
            return self['users'][userid]['groups']
        except (KeyError, IndexError):
            return []

    def put_user_in_group(self, userid, group, value):
        self[f'user:{userid}:{group}'] = value

        with self.mutable('users') as users:
            user = users.get(userid)
            if user:
                user['groups'].append(group)
            else:
                users[userid] = {
                    'groups': [group],
                }

        with self.mutable('groups') as groups:
            if group in groups.keys():
                groups[group]['members'].append(userid)
            else:
                groups[group] = {
                    'members': [userid],
                    'at': datetime.datetime.now().isoformat(),
                    'by': userid,
                }
