import logging
import datetime
from errbot import BotPlugin, botcmd

log = logging.getLogger('errbot.groups')

class Groups(BotPlugin):
    """
    Handle groups
    """

    def activate(self):
        super().activate()

        # Initialize Gutils
        self.gutils = self.get_plugin('gutils')

    @botcmd
    def group_in(self, msg, args):
        '''Usage: .group in [group] - List groups you're in or specify a group
        to get more details.'''
        args = args.strip().split()
        if args:
            user = self.gutils._get_user_group(msg.frm.userid, args[0])
            if not user:
                return f'You are not in group {args[0]}.'
            else:
                by = self._bot.userid_to_username(user['by_id'])
                on = user['timestamp'].split('.')[0].replace('T', ' ')
                return (
                    f'You were added to **{args[0]}** '
                    f'on **{on}** by **@{by}**'
                )
        else:
            groups = self.gutils.get_groups_of_user(msg.frm.userid)
            if not groups:
                return 'You are not in any groups :disappointed:'
            return ', '.join(groups)

    @botcmd
    def group_list(self, msg, args):
        '''Usage: .group list - List all groups'''
        msg = ['List of groups:']
        for group, info in self.gutils.read_key('groups').items():
            msg.append(f"**`{group}`** ({len(info['members'])} members)")

        if len(msg) == 1:
            msg.append('None :disappointed:')

        return '\n\n'.join(msg)

    @botcmd
    def group_add(self, msg, args):
        '''Usage: .group add @username <group> - Add username to group'''
        target_nick = args.strip().split()[0]
        group = args.strip().split()[1].lower()

        if not group.isalpha():
            return 'Group name should be alphanumeric.'

        if not self.gutils._can_add_to_group(msg.frm.userid, group):
            self.gutils.audit(msg.frm.userid, 'group_add_attempt_fail', group)
            return f'You do not have rights to add to {group}.'

        target_uid = self._bot.username_to_userid(target_nick)

        if self.gutils.is_user_in_group(target_uid, group):
            return f'{target_nick} is already in `{group}`.'

        extras = {
            'timestamp': datetime.datetime.now().isoformat(),
            'by_id': msg.frm.userid,
            'by_username': msg.frm.nick,
        }
        self.gutils.audit(msg.frm.userid, 'group_added', group, target_uid)
        self.gutils.put_user_in_group(target_uid, group, extras)

        return f'{target_nick} added to group {group}'
