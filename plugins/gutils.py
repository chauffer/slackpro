import logging
import datetime
from errbot import BotPlugin, botcmd

log = logging.getLogger('errbot.gutils')

class Gutils(BotPlugin):
    """Groups utils"""

    def activate(self):
        super().activate()
        db_items = (
            ('groups', dict),
            ('users', dict),
            ('channel_to_groups', dict),
            ('group_to_channels', dict),
            ('audit_incr', int),
        )

        # Initialize DB
        for key, method in db_items:
            try:
                _ = self[key]
            except KeyError:
                self[key] = method()

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

    def get_users_of_group(self, group):
        try:
            if group not in self['groups']:
                return None
            return self['groups'][group]['members']
        except (KeyError, IndexError):
            return None

    def put_user_in_group(self, userid, group, extras):
        self[f'user:{userid}:{group}'] = extras

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
        self.autoinvite_handle_user(group, userid)

    def get_channels_of_group(self, group):
        if group not in self['group_to_channels'].keys():
            return []
        return self['group_to_channels'][group]

    def get_channels_of_user(self, userid):
        channels = []
        for group in self.get_groups_of_user(userid):
            channels += self.get_channels_of_group(group)
        return channels

    def get_channel(self, channel, group):
        try:
            return self[f'channel_share:{channel}:{group}']
        except:
            return None

    def autoinvite_handle_user(self, group, userid):
        for channel in self.get_channels_of_group(group):
             if self.get_channel(channel, group).get('autoinvite'):
                self._bot.query_room(channel).invite(userid)

    def autoinvite_handle_channel(self, group, channel):
        for user in self.get_users_of_group(group):
             if self.get_channel(channel, group).get('autoinvite'):
                 for userid in self.get_users_of_group(group):
                     self._bot.query_room(channel).invite(userid)

    def share_channel(self, userid, channel, group, data):
        self[f'channel_share:{channel}:{group}'] = data

        with self.mutable('channel_to_groups') as d:
            if channel in d.keys():
                d[channel].append(group)
            else:
                d[channel] = [group]

        with self.mutable('group_to_channels') as d:
            if group in d.keys():
                d[group].append(channel)
            else:
                d[group] = [channel]
