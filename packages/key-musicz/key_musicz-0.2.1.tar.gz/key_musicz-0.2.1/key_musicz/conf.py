#
from buildz import xf, fz, pyz, dz, Args, Base
import os
from . import playz, keyz
def fetch(keys, as_list = False):
    if type(keys) not in (list,tuple):
        #print(f"return not list", keys, as_list)
        if as_list:
            return [keys]
        return keys
    if as_list:
        rst = []
        for it in keys:
            rst+=fetch(it, as_list)
        #print("return list:", rst)
        return rst
    if len(keys)==2:
        if type(keys[0]) not in (list, tuple, dict) and keys[0]!='vals':
            rst = {}
            rst[keys[0]] = keys[1]
            return rst
        elif keys[0]=='vals' or (keys[0][0]=='vals' and len(keys[0])==1):
            rst = []
            for it in keys[1]:
                rst+= fetch(it, as_list)
            return rst
        elif keys[0][0] == 'vals':
            rst = [fetch(it, True) for it in keys[1]]
            ks = keys[0][1:]
            out = []
            for it in rst:
                tmp = {}
                for k,v in zip(ks, it):
                    tmp[k] = v
                out.append(tmp)
            return out
    temp = {}
    arr = []
    for it in keys:
        tmp = fetch(it, as_list)
        if type(tmp) == dict:
            temp.update(tmp)
        else:
            arr += tmp
    if len(arr)==0:
        return temp
    out = []
    for it in arr:
        dt = dict(temp)
        dt.update(it)
        out.append(dt)
    return out
def fetch_cmds(ks):
    #print(f"fetch_cmds: {ks}")
    if isinstance(ks, Args):
        ks = ks.as_list(cmb=0, item_args = False, deep=True)
    cmds = []
    for it in ks:
        cs = fetch(it)
        if type(cs) == dict:
            cs = [cs]
        cmds+=cs
    return cmds

def init(fps, sys_conf={}):
    confs = [xf.loadxf(fp, as_args=True,spc=False) for fp in fps]
    if len(confs)>0:
        conf = confs[0]
    else:
        conf = {}
    for it in confs[1:]:
        dz.deep_fill_argx(it, conf, 1)
    dz.deep_fill_argx(sys_conf, conf, 1)
    if isinstance(conf, Args):
        conf = conf.dicts
    ks, vs, inits, trs, save= dz.g(conf, keys=[], vars={}, init={}, transforms={}, save = {})
    # if isinstance(ks, Args):
    #     ks = ks.as_list(cmb=0, item_args = False, deep=True)
    if isinstance(vs, Args):
        vs = vs.as_dict(True)
    if isinstance(inits, Args):
        inits = inits.as_dict(True)
    if isinstance(trs, Args):
        trs = trs.as_dict(True)
    if isinstance(save, Args):
        save = save.as_dict(True)
    # cmds = []
    # for it in ks:
    #     cs = fetch(it)
    #     if type(cs) == dict:
    #         cs = [cs]
    #     cmds+=cs
    cmds = fetch_cmds(ks)
    # print("orders:", cmds)
    # print("vars:", vs)
    # print("init:", inits)
    return cmds, vs, inits, trs, save

pass
class Orders(Base):
    def init(self):
        self.orders = {}
    def set(self, key, fc):
        self.orders[key] = fc
    def call(self, maps, *args):
        maps = dict(maps)
        key = maps['action']
        del maps['action']
        return self.orders[key](*args, **maps)

pass
from .base import default_src, conf_fp, path
class Conf(Base):
    def win_fix(self, libpath):
        #print(f"[TESTZ] libpath: {libpath}")
        if libpath is None:
            return
        import os
        if hasattr(os, 'add_dll_directory'):  # Python 3.8+ on Windows only
            os.add_dll_directory(libpath)
            os.environ['PATH'] += f';{libpath}'
    def init(self, fps, sys_conf={}):
        self.to_stops = set()
        if type(fps) not in (list, tuple):
            fps = [fps]
        #self.play = play
        #print(f"[TESTZ] sys_conf: {sys_conf}")
        self.fps = fps
        cmds, vs, inits, trs, saves = init(fps, sys_conf)   
        #print(f"[TESTZ] inits: {inits}")
        sfile, fps, select, sample_rate, libpath = dz.g(inits, sfile = default_src, fps=30, select={}, sample_rate=44100, libpath=None)
        sfile = path(sfile)
        libpath = path(libpath)
        self.win_fix(libpath)
        sfile = sfile or default_src
        if sfile is None or not os.path.isfile(sfile):
            print(f"ERROR: sf2文件'{sfile}'不存在 / sf2 file '{sfile}' not exists")
            exit()
        play = playz.Play(sfile,fps=fps, sample_rate=sample_rate)
        play.select(**select)
        channel = dz.g(select, channel= 0)
        self.channel= channel
        self.play = play
        self.ks = keyz.Keys(self.press_callback)
        self.vars = vs
        self.baks = {}
        self.trs = trs
        self.save_fp = None
        if dz.g(saves, work=0):
            self.save_fp = dz.g(saves, filepath="%Y%m%d%H%M%S.wav")
        rst = {}
        for cmd in cmds:
            key = str(cmd['key'])
            rst[key] = [cmd]
        self.keys = rst
        #print(f"keys:", list(self.keys.keys()))
        self.build_fc()
        self.running = True
    def start(self):
        self.running = True
        self.play.start()
        self.ks.start()
    def close(self):
        self.ks.stop()
        self.play.stop()
        self.play.close(self.save_fp)
    def stop(self,*a,**b):
        for n in self.to_stops:
            self.play.unpress(n, self.channel)
        self.to_stops = set()
    def quit(self, *a, **b):
        self.running = False
        input("press enter to quit:\n")
    def wait(self):
        import time
        while self.running:
            time.sleep(0.1)
    def press(self, do_press, label, var, val, **maps):
        if do_press:
            bak = self.vars[label][var]
            dz.dset(self.baks, [label, var], bak)
            self.vars[label][var] = val
        else:
            bak = self.baks[label][var]
            self.vars[label][var] = bak
    def move_base(self, do_press, label, var, val, **_):
        if do_press:
            #bak = self.vars[label][var]
            #dz.dset(self.baks, [label, var], bak)
            #print(f"before press self.vars[{label}][{var}]: {self.vars[label][var]}")
            self.vars[label][var] += val
            #print(f"after press self.vars[{label}][{var}]: {self.vars[label][var]}")
        else:
            #print(f"before unpress self.vars[{label}][{var}]: {self.vars[label][var]}")
            self.vars[label][var] -= val
            #print(f"after unpress self.vars[{label}][{var}]: {self.vars[label][var]}")
        pass
    def change(self, do_press, label, var, val, **_):
        if not do_press:
            return
        self.vars[label][var] = val
    def mode(self, do_press, mode, **_):
        self.vars['mode'] = mode
    def fix_power(self, n,power):
        vmin = dz.dget(self.vars, 'soundfix.min'.split("."), 0)[0]
        vmax = dz.dget(self.vars, 'soundfix.max'.split("."), 0)[0]
        vdst = vmax-vmin
        n = min(max(n, 36), 132)
        rate = (n-36)/(132-36)
        #rate=rate*rate
        v = int(power+vmin+vdst*rate)
        #print(f"sound for {n}: {v}")
        return v
    def change_mode(self, do_press, *a, **b):
        #print(f"call change_mode: {do_press}, {a}, {b}")
        if not do_press:
            return
        self.vars['mode'] = 1-self.vars['mode']
        print(f"mode: {self.vars['mode']}")
    def push_conf(self, do_press, conf, **_):
        conf = xf.loadx(conf, as_args=True,spc=False)
        #print(f"conf: {conf}")
        cmds = fetch_cmds(conf)
        #print(f"cmds: {cmds}")
        #print(f"press push_conf: {do_press}")
        #return
        keys = self.keys
        for cmd in cmds:
            key = str(cmd['key'])
            if key not in keys:
                keys[key] = []
            #print(f"key: {key}, keys: {keys[key]}")
            #continue
            if do_press:
                keys[key].append(cmd)
            else:
                keys[key].pop(-1)
    def sound(self, do_press, label, sound, power=None, **_):
        vs = self.vars[label]
        n = vs['base']+sound
        if not do_press:
            if self.vars['mode']==0:
                self.play.unpress(n, self.channel)
                if n in self.to_stops:
                    self.to_stops.remove(n)
            return
        if power is None:
            power = vs['power']
        if n in self.to_stops:
            self.play.unpress(n, self.channel)
            self.to_stops.remove(n)
        power = self.fix_power(n, power)
        #print(f"play.press({n}, {power})")
        self.play.press(n, power, self.channel)
        self.to_stops.add(n)
    def press_callback(self, char, press):
        #print(f"press:", char, press)
        if char in self.trs:
            char = str(self.trs[char])
        #print(f"press1:", char, press)
        if char not in self.keys:
            return
        maps = self.keys[char][-1]
        self.orders(maps, press)
    def build_fc(self):
        self.orders = Orders()
        self.orders.set('press', self.press)
        self.orders.set('stop', self.stop)
        self.orders.set('mode', self.mode)
        self.orders.set('quit', self.quit)
        self.orders.set('change', self.change)
        self.orders.set('sound', self.sound)
        self.orders.set('push_conf', self.push_conf)
        self.orders.set('change_mode', self.change_mode)
        self.orders.set('move_base', self.move_base)


from buildz import argx
s_help = fz.fread(path("help.txt")).decode("utf-8")
def test():
    import time,sys
    ft = argx.Fetch(*xf.loads("[fp,sfile,libpath,default,help],{f:fp,s:sfile,l:libpath,t:default,h:help}"))
    rst = ft(sys.argv[1:])
    if 'help' in rst:
        print(s_help)
        return
    fps = []
    if 'fp' in rst:
        fps.append(path(rst['fp']))
        del rst['fp']
    default = '1'
    if 'default' in rst:
        default = rst['default']
        del rst['default']
    if default in (0,'0'):
        default = None
    elif default in (1,'1'):
        default = conf_fp
    if default:
        fps = [path(default)]+fps
    sys_conf = {'init':rst}
    conf = Conf(fps, sys_conf)
    conf.start()
    print("run success, enter '~' to quit")
    print("运行中,按下'~'键来退出")
    conf.wait()
    print("release")
    conf.close()

pass

pyz.lc(locals(), test)
'''
python -m key_musicz.run -dD:\rootz\python\gits\key_musicz\lib
'''