#coding=utf-8

from pynput.keyboard import Listener, Key
# 存在的控制按键
ckeys = ['alt', 'alt_gr', 'alt_l', 'alt_r', 'backspace', 'caps_lock', 'cmd', 'cmd_r', 'ctrl', 'ctrl_l', 'ctrl_r', 'delete', 'down', 'end', 'enter', 'esc', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'home', 'insert', 'left', 'media_next', 'media_play_pause', 'media_previous', 'media_volume_down', 'media_volume_mute', 'media_volume_up', 'menu', 'num_lock', 'page_down', 'page_up', 'pause', 'print_screen', 'right', 'scroll_lock', 'shift', 'shift_r', 'space', 'tab', 'up']
# 转换后的控制按键名称
skeys = ['alt_l', 'alt_r', 'alt_l', 'alt_r', 'backspace', 'caps_lock', 'cmd', 'cmd_r', 'ctrl_l', 'ctrl_l', 'ctrl_r', 'delete', 'down', 'end', 'enter', 'esc', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'home', 'insert', 'left', 'media_next', 'media_play_pause', 'media_previous', 'media_volume_down', 'media_volume_mute', 'media_volume_up', 'menu', 'num_lock', 'page_down', 'page_up', 'pause', 'print_screen', 'right', 'scroll_lock', 'shift_l', 'shift_r', 'space', 'tab', 'up']
ckeys2s = {}
for k,v in zip(ckeys,skeys):
    if hasattr(Key, k):
        ckeys2s[getattr(Key,k)] = v

pass
from buildz import Base
import threading
class Keys(Base):
    def char(self, key):
        if key in ckeys2s:
            return ckeys2s[key]
        if hasattr(key, "char"):
            return key.char
        return None
    def stop(self):
        self.lst.stop()
    def init(self, fc=None):
        '''
            callback: fc(char, press=bool)
        '''
        self.th = None
        self.fc = fc
        self.keys= set()
    def press(self, key):
        #print("press", key)
        c = self.char(key)
        #print("press c:", c)
        if c is not None:
            if c in self.keys:
                return
            self.keys.add(c)
            self.fc(c, True)
    def release(self, key):
        c = self.char(key)
        if c is not None:
            if c in self.keys:
                self.keys.remove(c)
            self.fc(c, False)
    def start(self):
        if self.th:
            return
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()
    def run(self):
        with Listener(on_press=self.press, on_release=self.release) as lst:
            self.lst = lst
            lst.join()

pass