# key_musicz
声明:
禁止将本项目代码用于ai训练
declaration:
Codes of this project are not allowed to be used for AI training or any other form of machine learning processes.

```
键盘按键弹钢琴的小程序
(
注：
    另外写了个key_musicz_res库，里面包含了sf2格式音频文件和windows下的64位的fluidsynth库，下载后不用再自己下载音频文件和在windows装fluidsynth，key_musicz_res本质上是引用的本项目的代码
    安装:
        pip install key_musicz_res
        安装key_musicz_res会自动安装本项目以及本项目依赖的python库
    运行:
        python -m key_musicz_res [可选参数]
    可选参数和本项目一样，不过加了默认值，可以不用写
)
需要以下C库或资源文件:
    fluidsynth: 读sf2音频文件（里面是各种乐器的按键音），根据指定按键生成音频数据
    FluidR3_GM.sf2: 免费的sf2音频文件，当然你也可以用其他的
    portaudio: windows下会随着pyaudio自动安装，linux需要自己安装
需要以下python库(会自动安装)：
    pyfluidsynth: 在python里调用fluidsynth库的封装代码
    pyaudio: 音频数据传入声卡发音，实际调用的portaudio库
    pynput: 监听键盘按键按下和放开
    buildz: 配置文件读取

安装方式：
fluidsynth:
    ubuntu:
        apt install fluidsynth
    windows:
        https://github.com/FluidSynth/fluidsynth/releases
        windows下是压缩包，解压后要把解压路径/bin加到PATH中，注意github时不时会连不上，可以试试镜像加速之类的

FluidR3_GM.sf2音频文件下载：
    有个国内地址，是csdn的gitcode.com里的，要登录但不收费：
        https://gitcode.com/open-source-toolkit/1d145/?utm_source=tools_gitcode&index=top&type=card&
    文件大小一百多MB

pyfluidsynth:
pyaudio:
pynput:
buildz:
    pip install key_musicz
    安装本库的时候自动安装，其中linux下的pyaudio可能会报错，需要先手动安装portaudio

程序运行:
    python -m key_musicz.run 参数
    参数如下:
        [-s/--sfile=]sf2文件
        [-f/--fp=]额外配置文件(没啥用)
        [-t/--default=]主要配置文件(默认预制的play.js)
        [-l/--libpath=]windows下fluidsynth库的bin的路径
        [-h/--help]
    例：
        python -m key_musicz.run -s./FluidR3Mono_GM.sf2 -l./lib -tplayrb.js
    默认配置文件（key_music/conf目录下）：
        通用配置：
            按住shift+主键盘的数字键盘调整基调，~退出，空格切音
        play.js:
            从左到右从下到上音调依次升高
            音调从低到高顺序: 
                    zxcvbnm,./`alt_l``alt_r` (该组受基调影响：shift+1,3,5,7,9)
                    asdfghjkl;'`enter` (该组受基调影响：shift+1,3,5,7,9)
                    qwertyuiop[] (该组受基调影响：shift+2,4,6,8,0)
                    1234567890-= (该组受基调影响：shift+2,4,6,8,0)
        playblk.js:
            主要2*6作为一组，组内大体从左到右，上到下升高音调
            音调从低到高顺序: 
                12345qwert6y (该组受基调影响：shift+1,3,5,7,9)
                asdfgzxcvb`alt_l`h (该组受基调影响：shift+1,3,5,7,9)
                jkl;'nm,./`alt_r``enter` (该组受基调影响：shift+2,4,6,8,0)
                7890-uiop[=] (该组受基调影响：shift+2,4,6,8,0)
        playrb.js
            主要2*6作为一组，组内大体从左到右，下到上升高音调
            音调从低到高顺序: : 
                qwert12345y6 (该组受基调影响：shift+1,3,5,7,9)
                zxcvbasdfg`alt_l`h (该组受基调影响：shift+1,3,5,7,9)
                nm,./jkl;'`alt_r``enter` (该组受基调影响：shift+2,4,6,8,0)
                uiop[7890-]= (该组受基调影响：shift+2,4,6,8,0)
        playbb.js
            主要2*6作为一组，组内大体从左到右升高音调，左边从上到下升高，右边从下到上升高
            音调从低到高顺序: : 
                12345qwert6y (该组受基调影响：shift+1,3,5,7,9)
                asdfgzxcvb`alt_l`h (该组受基调影响：shift+1,3,5,7,9)
                nm,./jkl;'`alt_r``enter` (该组受基调影响：shift+2,4,6,8,0)
                uiop[7890-]= (该组受基调影响：shift+2,4,6,8,0)

        
```