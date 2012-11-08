#!/usr/bin/python
# encoding=utf-8

import threading
import pyglet.app
import pyglet.media
import pyglet.clock

import douban

class Player(threading.Thread):

    playing = False
    song = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.douban = douban.Douban()
        self.player = pyglet.media.Player()
        @self.player.event
        def on_eos():
            if self.song:
                self.song.time = self.song.length
            song = self.douban.next(self.song)
            self.play(song)

    # 该方法会阻塞
    def run(self):
        pyglet.app.run()

    def next(self):
        if self.song:
            self.song.time = self.player.time
        song = self.douban.next(self.song)
        self.play(song)

    def pause(self):
        self.playing = False
        self.player.pause()

    def play(self, song = None):
        self.playing = True
        if not song and self.song:
            self.player.play()
            return
        elif not song:
            song = self.douban.next()

        # for test
        if type(song) == str:
            f = song
            song = douban.Song()
            song.file = f

        self.song = song
        self.player.pause()
        self.player.next()
        source = pyglet.media.load(song.file or song.url)
        self.player.queue(source)
        self.player.play()

    def like(self):
        self.song.time = self.player.time
        self.douban.like(self.song)

    def unlike(self):
        self.song.time = self.player.time
        self.douban.unlike(self.song)

    def exit(self):
        pyglet.app.exit()


# 这一行代码是必需的
# pyglet 是由 pyglet.app.run() 进行实际的播放
# 而该方法最后实际上是一个 select 循环
# 
# while True:
#   select.select(displays,(),(),waitTime)
#   ... ...
#
# displays 是所有的可显示的对象，比如窗口
# 本程序没有那些东西，所以就变成了
# 
# while True:
#   select.select((),(),(),waitTime)
#   ... ...
#
# waitTime 与 clock 有关
# clock 会调度一些需要在未来执行的方法
# waitTime = clock 下一次调度的时间 - 当前时间
#
# 本程序需要调度的方法只是播放，当暂停时，他会被取消调度
# 这样 clock 就没有需要调度的东西了
# 此时：
# waitTime = None
# 
# while True:
#   select.select((),(),(),None)
#   ... ...
#
# 然后，就没有然后了 ...
pyglet.clock.schedule_interval_soft(lambda dt:None, 0.09)


if __name__ == "__main__":
    p = Player()
    p.play()
    p.run()
