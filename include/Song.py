import pafy
import vlc

# VLC Player
class Song():
    def __init__(self, url = '', file = False):
        if not file:
            self.url = url
            self.best_url = pafy.new(url).getbestaudio().url
            self.media = vlc.MediaPlayer(self.best_url)
        else:
            self.media = vlc.MediaPlayer('/tmp/ts3musicbot.mp3')

    def play(self):
        self.media.play()

    def stop(self):
        self.media.stop()

    def pause(self):
        self.media.pause()

    def volume(self, vol):
        self.media.audio_set_volume(vol)

    def skip(self, forward):
        length = self.media.get_length()/1000
        position = self.media.get_position()

        position_s = length * position
        new_position_s = position_s + forward

        new_position = new_position_s / length
        self.media.set_position(new_position)
