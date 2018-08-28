import json
import time

import irc.bot

irc.client.ServerConnection.buffer_class.errors = 'replace'

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.oplist = self.get_oplist()

    def update_oplist(self, c, channels='all'):
        if channels == 'all':
            channels = [i for i in self.oplist]
        for channel in channels:
            chan = self.channels[channel]
            ops = chan.opers()
            users = chan.users()
            if channel not in self.oplist:
                self.oplist[channel] = {'ops': []}
            for op in ops:
                if op not in self.oplist[channel]['ops']:
                    self.oplist[channel]['ops'].append(op)
        self.write_oplist()

    def give_ops(self, c, channel):
        chan = self.channels[channel]
        ops = chan.opers()
        users = chan.users()
        for user in users:
            if user in self.oplist[channel]['ops'] and user not in ops:
                c.mode(channel, '+o {}'.format(user))
                time.sleep(0.5)

    def get_oplist(self):
        with open('oplist.json') as o:
            oplist = json.load(o)
        return oplist

    def write_oplist(self):
        with open('oplist.json', 'w') as o:
            json.dump(self.oplist, o, indent=2)

    def on_welcome(self, c, e):
        for channel in self.oplist:
            c.join(channel)

    def on_pubmsg(self, c, e):
        text = e.arguments[0]
        cmd = text.split(' ')[0]
        if cmd == '!update':
            self.update_oplist(c, [e.target])
        elif cmd == '!updateall':
            self.update_oplist(c)

    def on_invite(self, c, e):
        c.join(e.arguments[0])

    def on_join(self, c, e):
        self.give_ops(c, [e.target])

    def on_mode(self, c, e):
        if e.source.nick == 'opbot':
            pass
        if e.arguments[0] == '-o' and e.arguments[1] in self.oplist[e.target]['ops']:
            self.oplist[e.target]['ops'].remove(e.arguments[1])
            self.write_oplist()
            self.update_oplist(c, [e.target])
        if e.arguments[0] == '+o':
            self.update_oplist(c, [e.target])


if __name__=='__main__':
    bot = Bot(
        nickname='opbot',
        server='localhost',
    )
    bot.start()

