# Parse commands to MusicBot
class Parse():
    def __init__(self, data):
        self.args = data.split(' ')
        self.args_num = len(self.args)

        if self.args[0] == '!yt' and self.args_num == 2:
            self.args[1] = self.args[1][5:-6]

