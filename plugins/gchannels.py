import logging
import datetime
from errbot import BotPlugin, botcmd

log = logging.getLogger('errbot.gchannels')


class Gchannels(BotPlugin):
    """
    Handle Groups channels
    """

    def activate(self):
        super().activate()

        # Initialize DB
        for i in ('channels_to_groups', 'groups_to_channels'):
            try:
                _ = self[i]
            except KeyError:
                self[i] = {}

        # Initialize Devaudit
        self.gutils = self.get_plugin('gutils')

    @botcmd
    def channel_share(self, msg, args):
        '''Usage: .channel share <group> [autoinvite]'''
        args = args.strip().split()

        channel, group = msg.frm.channelid, args[0]
        autoinvite = bool(len(args) >= 2 and 'autoinvite' in args[1])

        self.gutils.audit(msg.frm.userid, 'channel_share_attempt', group, channel)

        if not self.gutils.is_user_in_group(msg.frm.userid, group):
            return 'You are not in that group.'

        try:
            _ = self[f'shared:{channel}:{group}']
        except KeyError:
            pass
        else:
            return f'Channel is already shared with {group}.'

        self[f'shared:{channel}:{group}'] = {
            'at': datetime.datetime.now().isoformat(),
            'by': msg.frm.userid,
            'autoinvite': autoinvite,
        }
        self.gutils.audit(msg.frm.userid, 'channel_share_success', group, channel)

        with self.mutable('channels_to_groups') as d:
            if channel in d.keys():
                d[channel].append(group)
            else:
                d[channel] = [group]

        with self.mutable('groups_to_channels') as d:
            if group in d.keys():
                d[group].append(msg.frm.channelid)
            else:
                d[group] = [msg.frm.channelid]

        return f'This channel was shared with {group}.'

    @botcmd
    def channel_list(self, msg, args):
        '''Usage: .channel list - Show channels your groups can join'''

        output = []
        for group in self.gutils.get_groups_of_user(msg.frm.userid):
            output.append(f'For group `{group}`, you can join:')

            for channel in self._get_channels_of_group(group):
                channel = self._bot.channelid_to_channelname(channel)
                output.append(f' - #{channel}')

            if not output:
                output.append('You can join Nothin.')

        return '\n'.join(output)

    @botcmd
    def channel_join(self, msg, args):
        '''Usage: .channel join <channel> - Join the channel'''
        args = args.strip().split()
        if not len(args):
            return 'Usage: .channel join <channel>'

        channel = self._bot.channelname_to_channelid(args[0])
        if channel not in self._get_channels_of_user(msg.frm.userid):
            return 'You cannot join that channel.'

        self._bot.query_room(channel).invite(msg.frm.nick)
        return 'Invited! :yay:'

    def _get_channels_of_group(self, group):
        if group not in self['groups_to_channels'].keys():
            return []
        return self['groups_to_channels'][group]

    def _get_channels_of_user(self, userid):
        channels = []
        for group in self.gutils.get_groups_of_user(userid):
            channels += self._get_channels_of_group(group)
        return channels
