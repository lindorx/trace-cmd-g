#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sys
import getopt
import datetime
import os
import time
import pickle
from pathlib import Path
from matplotlib.pyplot import MultipleLocator
# 小数截取


def cutdec(number1, num):
    return float(str(number1).split('.')[0]+'.'+str(number1).split('.')[1][:num])

# 进度条，percent要大于0


def process_bar(percent, start_str='', end_str='', total_length=0):
    bar = ''.join(["\033[31m%s\033[0m" % '#'] *
                  int(percent * total_length)) + ''
    bar = '\r' + start_str + \
        bar.ljust(int(percent*total_length)) + \
        ' {:0>4.1f}%|'.format(percent*100) + end_str
    print(bar, end='', flush=True)

# 统计数据
# tracedatl：一个3*n的数组，tracedatl[0]为所在cpu，tracedatl[1]为采样时间，tracedatl[2]为函数名
# timesec：统计间隔数组
# funnames：函数名数组，为tracedatl[2]中所有存在的函数


def statistical_data(tracedatl, timesec, event):
    # 创建一个二维数组，用于记录每个函数在每秒的执行次数
    funnamenum = np.zeros(
        [np.max(tracedatl[0])+1, len(event), len(timesec)], dtype=int, order='C')
    # 统计每个函数在每秒出现的时间，并置入funnamenum
    # x表示行，y表示列
    x, y, item = 0, 1, 0
    tmp1 = int(len(tracedatl[1])/100)
    for i in tracedatl[1]:
        if i > timesec[y]:
            y += 1
        # 逐个判断函数名
        x = 0
        for name in event:
            if name == tracedatl[2][item]:
                # 找到文件名，令其在funnamenum数组中对应的值加一
                funnamenum[tracedatl[0][item]][x][y] += 1
                break
            x += 1
        item += 1
        if item % tmp1 == 0:
            process_bar(item/tmp1/100, start_str='',
                        end_str='100%', total_length=60)
    print()
    return funnamenum

# linedata:曲线数据，即y轴；timesec：时间刻度，即x轴
# picturefile：保存路径；funnames：函数名数组；line_range：x轴范围；time_intervial：时间间隔；one_picture：图形分离标志；plot_display：图形显示标志


def save_show_picture(linedata, timesec, picturefile, event, line_range, time_intervial=1, one_picture=True, plot_display=False):
    #fig, ax = plt.subplots(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
    if one_picture:  # 将所有函数曲线放到一起
        count = 0
        plt.figure(num=1, figsize=(20, 5))
        for curve in linedata:
            plt.plot(timesec[line_range[0]:line_range[1]],
                     curve[line_range[0]:line_range[1]], label=str(event[count], 'ascii'))
            plt.legend()
            count += 1
        picturefile += '.jpg'
        plt.savefig(picturefile)
        print('图片保存至\''+picturefile+'\'')
    else:  # 将函数曲线分为多个图片
        count = 0
        for curve in linedata:
            plt.figure(figsize=(20, 5))
            plt.title(event[count])
            plt.plot(timesec[line_range[0]:line_range[1]],
                     curve[line_range[0]:line_range[1]])
            picture1 = picturefile+'-'+str(event[count], 'ascii')+'.jpg'
            plt.savefig(picture1)
            print('图片保存至\''+picture1+'\'')
            count += 1

    x_major = MultipleLocator(time_intervial)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major)
    if plot_display:
        plt.show()


parameter_cmd = {'show_picture': ['show'], 'show_timesec': ['timeax', 'ta'],
                 'show_event': ['event', 'e'], 'show_function_count': ['funs'],
                 'clear': ['cle', 'clear'], 'help': ['help', 'h'],
                 'show_fun':['fun','f']}


def _cmd_1(linedata, timesec, event, funnamenum, line_range):
    time_intervial = 0.1
    yn = input("\n是否进入命令(Y/n)：")
    if yn != '' and yn != 'y' and yn != 'Y':
        exit(1)
    print("===========================================================")
    my_string = input(">>")
    while my_string != 'q' and my_string != 'quit':
        if my_string in parameter_cmd['show_picture']:
            # 按照默认值展示图片
            count = 0
            plt.figure(figsize=(20, 5))
            # 绘制全部曲线数据
            for curve in linedata:
                plt.plot(timesec[line_range[0]:line_range[1]],
                         curve[line_range[0]:line_range[1]], label=event[count])
                plt.legend()
                count += 1
            # 打开图片
            x_major = MultipleLocator(time_intervial)
            ax = plt.gca()
            ax.xaxis.set_major_locator(x_major)
            plt.show()
            plt.close()
            plt.clf()
        elif my_string in parameter_cmd['show_event']:
            # 打印所有事件名
            print(event)
        elif my_string in parameter_cmd['show_fun']:
            #打印所有函数
            print()
        elif my_string in parameter_cmd['show_timesec']:
            # 打印时间轴
            print(timesec)
        elif my_string in parameter_cmd['clear']:
            # 清空屏幕
            os.system('clear')
        elif my_string in parameter_cmd['show_function_count']:
            # 显示数据
            print(funnamenum)
        elif my_string in parameter_cmd['help']:
            # 显示帮助
            print(list(parameter_cmd.values()))
        elif my_string == '\n':
            continue
        else:
            print("命令不合法！")
        my_string = input(">>")


def get_picture(tracedatl, picturefile, time_intervial, one_picture, plot_display, cpus=[], fun_list=[], line_range=[], open_cmd=False):
    event = np.unique(tracedatl[2])
    # 创建秒间隔数组
    timesec = [cutdec(i, 6) for i in np.linspace(cutdec(tracedatl[1][0], 2), cutdec(tracedatl[1][-1], 2)+2*time_intervial,
                                                 int((cutdec(tracedatl[1][-1], 2)-cutdec(tracedatl[1][0], 2)+2*time_intervial)/time_intervial)+1)]
    if line_range == []:
        line_range = [1, len(timesec)-2]  # 两端的统计是不准确的，所以去掉
    funnamenum = statistical_data(tracedatl, timesec, event)
    # 将所有cpu上的统计结果相加，获得整个进程的结果
    allcpufun = sum(funnamenum)
    if cpus == []:
        save_show_picture(allcpufun, timesec, picturefile, event,
                          line_range, time_intervial, one_picture, plot_display)
    else:
        for i in cpus:
            save_show_picture(funnamenum[i], timesec, picturefile+'-'+str(
                i), event, line_range, time_intervial, one_picture, plot_display)
    if open_cmd:
        # 进入命令处理程序
        _cmd_1(allcpufun, timesec, event, funnamenum, line_range)


def dat2tmp(datfile, tmpfile):
    #检查文件是否存在
    datfile_path=Path(datfile)
    if not datfile_path.is_file():
        print('文件\''+datfile+'\'不存在')
        exit(1)
    start = datetime.datetime.now()
    # 使用shell将trace-cmd采样的数据转换为可识别的格式
    print("生成临时文件中。。。")
    shell_script = 'trace-cmd report -i '+datfile + \
        ' | awk \'match($0,/\\[(...)\\].+(....\\.......): (.+): .+/,a){printf(\"%s %s %s\\n\",a[1],a[2],a[3])}\' > ' + tmpfile
    os.system(shell_script)
    end = datetime.datetime.now()
    print("临时文件保存于\'"+tmpfile+'\' 花费时间' +
          str((end-start).total_seconds())+'秒')
    return tmpfile

# 将读取的文件转换为数组变量存入文件，以加快读取速度
# 返回转换好的数据


def tmp2var(tmpfile, varfile):
    print("整理数据中。。。")
    try:
        with open(tmpfile, 'rb') as fin:
            tracedatl = list(
                zip(*([[int(i.split()[0]), float(i.split()[1]), i.split()[2]] for i in fin])))
            with open(varfile, 'wb') as varfout:
                pickle.dump(tracedatl, varfout)
    except OSError as fileerror:
        print("文件打开失败：\'")
        print(fileerror)
    return tracedatl


def readvar(varfile):
    print("读取数据中。。。")
    try:
        with open(varfile, 'rb') as fin:
            tracedatl = pickle.load(fin)
    except OSError as error1:
        print('打开文件：\''+varfile+'\'失败')
        print(error1)
        exit(1)
    return tracedatl

# 主函数
# -h | --help ：帮助
# -i | ifile= : 输入文件（trace-cmd record生成的文件）
# -o | ofile= : 输出文件（输出为图片，默认为执行路径）
# -s | --split : 分成多张图片（与'-a'冲突）
# -a | --all : 将曲线图合并为一张（默认，与'-s'冲突）
# -t | --tmpfile : 缓存文件，默认以data结尾，存入/tmp目录
# -S | --Scale : 统计的时间间隔
# -d | --display : 展示由pyplot生成的图形
# -c | --cpu : 指定cpu
# -r | --range : 指定范围
# -v | --varfile : 指定变量文件
# -e : 指定统计事件
# -g : 指定统计函数
# --build-tmp ： 仅生成tmp文件
# --cmd ： 进入命令处理程序


def main(argv):
    inputfile = ''
    outputfile = ''
    tmpfile = ''
    one_picture = True
    time_intervial = 0.1
    plot_display = False
    cpus = []
    line_range = []
    open_cmd = False
    varfile = ''
    trace_date = []
    fun_list = []
    try:
        opts, args = getopt.getopt(argv, 'ac:dg:r:sht:i:o:S:v:', [
                                   'all', 'cpu=', 'display', 'split', 'help', 'varfile', 'tmpfile=', 'ifile=', 'ofile=', 'Scale', 'build-tmp', 'cmd'])
    except getopt.GetoptError as error:
        # 未找到参数
        print(error)
        print('trace-cmd-g.py -i <file.dat> -o <file.jpg>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):  # -h：帮助
            print('trace-cmd-g.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-a", "--all"):
            one_picture = True
        elif opt in ("-s", "--split"):
            one_picture = False
        elif opt in ("-t", "--tmpfile"):
            tmpfile = arg
        elif opt in ("-S", "--Scale"):
            time_intervial = float(arg)
        elif opt in ("-d", "--display"):
            plot_display = True
        elif opt in ("-c", "--cpu"):
            cpus = [int(i) for i in arg.split(',')]
        elif opt in ("-r", "--range"):
            line_range = [int(i) for i in arg.split(',')]
            if len(line_range) > 2:
                print("'-r'只能指定两个参数： -r 起始下标,结束下标")
                exit(5)
        elif opt in ("--build-tmp"):
            if inputfile != '':
                tmpfile = os.path.splitext(inputfile)[0]+'.tmp'
                dat2tmp(inputfile, tmpfile)
                exit(0)
        elif opt in ("--cmd"):
            open_cmd = True
        elif opt in ("-v", "--varfile"):
            varfile = arg
        elif opt in ("-g"):
            fun_list = [i for i in arg.split(',')]

    if varfile == '':
        if tmpfile == '':
            if inputfile == '':
                print("未指定输入文件")
                exit(1)
            else:
                filename1 = os.path.splitext(inputfile)[0]
                tmpfile= filename1+'.tmp'
                varfile=filename1+'.var'
                tracedatl = tmp2var(dat2tmp(inputfile,tmpfile),varfile)
        else:
            filename1 = os.path.splitext(tmpfile)[0]
            varfile= filename1+'.var'
            tracedatl = tmp2var(tmpfile,varfile)
    filename1 = os.path.splitext(varfile)[0]
    tracedatl = readvar(varfile)
    # 处理输出文件
    if outputfile == '':
        get_picture(tracedatl, filename1, time_intervial, one_picture,
                    plot_display, cpus=cpus, fun_list=fun_list, line_range=line_range, open_cmd=open_cmd)
    else:
        get_picture(tracedatl, os.path.splitext(outputfile)[
                    0], time_intervial, one_picture, plot_display, cpus=cpus, fun_list=fun_list, line_range=line_range, open_cmd=open_cmd)


if __name__ == '__main__':
    start = datetime.datetime.now()
    main(sys.argv[1:])
    end = datetime.datetime.now()
    print('时长'+str((end-start).total_seconds()))
