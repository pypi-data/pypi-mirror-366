vars: {
    left: {
        base: 48 // 0-127
        power: 90 // 0-127
    }
    right: {
        base: 72
        power: 90
    }
    soundfix: {
        // 按键音声音大小调整，相同声音大小下，低音听起来声音更大，引入修改量，低音到高音对应 min到max
        min: -5
        max: 5
    }
    mode: 1 //按键模式，1是按键松开后继续播放按键声音，0是松开后立刻停止按键声音
}
init: {
    select: {
        channel: 0 // MIDI通道号（0-15），9号通道通常预留给打击乐, 0是钢琴
        bank: 0 //音色库编号（0-16383），GM标准中0为常规乐器，128为打击乐
        preset: 0//音色编号（0-127），对应SoundFont(sf2文件)中的预设程序
    }
    sample_rate: 44100 //采样频率，这个应该要和sf2文件的实际频率保持一致，一般就是44100
    sfile: null // sf2音频文件路径，本地测试用的FluidR3Mono_GM.sf2（不知道和FluidR3_GM.sf2有什么不同，反正都是网上下的免费资源）
    libpath: null //fluidsynth库路径，在windows下没有在PATH配置fluidsynth路径时使用
    fps: 30 // 按键监听fps
}
keys: {
    // 左右shift实际没用，后续改改
    (
        action(press)
        var(power)
        vals(key, label, val): [
            left shift: (left, 120)
            right shift: (right,120)
        ]
    )
    //瞬间停止声音播放
    action(stop):{
        key:space
    }
    (
        // 退出
        action(quit)
        // 当前配置是按下shift+'`'（也就是'~'）退出程序
        key: '~'
    )
    // 左右键盘按键音基调，默认配置通过按键盘上的1-5改变左边按键基调，6-0改变右边按键基调
    action(change):{
        var(base)
        vals:{
            label(left): {
                vals(key, val): {
                    // !: 24,
                    // @: 36
                    // '#': 48
                    // $: 60
                    // %: 72
                    !:12
                    '#':24
                    %: 36
                    &:48
                    '(':60
                }
            }
            label(right):{
                vals(key, val): {
                    @:36
                    $:48
                    ^: 60
                    *: 72
                    ')':84

                    // ^: 48
                    // &: 60
                    // *: 72
                    // '(': 84
                    // ')': 96
                }
            }
        }
    }
    // 按键配置，默认左边qwertasdfgzxcvb，右边yuiophjkl;nm,./
    action(sound): {
        label(left): {
            vals(key,sound): {
                z=0,x=1,c=2,v=3,b=4,n=5,m=6,','=7,'.'=8,'/'=9,alt_l=10,alt_r=11,
                a=12,s=13,d=14,f=15,g=16,h=17,j=18,k=19,l=20,';'=21,"'"=22,'\\'=23,
            }
        }
        label(right): {
            vals(key, sound): {
                q=0,w=1,e=2,r=3,t=4,y=5,u=6,i=7,o=8,p=9,'['=10,']'=11,
                1=12,2=13,3=14,4=15,5=16,6=17,7=18,8=19,9=20,0=21,'-'=22,'+'=23
            }
        }
    }
    action(mode): {
        vals(key, mode): {
            // 切换按键音停止模式，0是松开按键立即停止按键音，1是松开按键继续播放按键音
            '_': 0
            '+': 1
        }
    }
    action(sound): {
        power(120)
        label(left): {
            vals(key,sound): {
                Q(0),W(1),E(2),R(3),T(4)
                A=5,S:6,D=7,F=8,G=9
                Z=10,X=11,C=12,V=13,B=14
            }
        }
        label(right): {
            vals(key, sound): {
                Y=0,U=1,I=2,O=3,P=4
                H=5,J=6,K=7,L=8,':'=9
                N=10,M=11,'<'=12,'>'=13,'?'=14
            }
        }
    }
}