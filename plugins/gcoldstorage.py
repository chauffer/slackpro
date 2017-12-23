from errbot import BotPlugin

class Gcoldstorage(BotPlugin):
    def store(self, key, value):
        self[key] = value
