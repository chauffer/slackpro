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

        # Initialize Gutils
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

        if self.gutils.get_channel(channel, group):
            return f'Channel is already shared with {group}.'

        data = {
            'at': datetime.datetime.now().isoformat(),
            'by': msg.frm.userid,
            'autoinvite': autoinvite,
        }
        self.gutils.share_channel(msg.frm.userid, channel, group, data)

        self.gutils.autoinvite_handle_channel(group, channel)
        self.gutils.audit(msg.frm.userid, 'channel_shared', group, channel)

        return f'This channel was shared with {group}.'

    @botcmd
    def channel_list(self, msg, args):
        '''Usage: .channel list - Show channels your groups can join'''

        output = []
        for group in self.gutils.get_groups_of_user(msg.frm.userid):
            output.append(f'For group `{group}`, you can join:')

            for channel in self.gutils.get_channels_of_group(group):
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
        if channel not in self.gutils.get_channels_of_user(msg.frm.userid):
            return 'You cannot join that channel.'

        self._bot.query_room(channel).invite(msg.frm.nick)
        return 'Invited! :yay:'
