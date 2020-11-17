#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import sys
import getopt
import datetime
import os
import time
import pickle
import re
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


# 全局变量
inputfile = ''  # 输入文件，后缀名“.dat”
outputfile = ''  # 输出文件，图片，后缀名“.jpg”，指定是无需指定后缀名
tmpfile = ''  # 中间文件，对“.dat”处理过的文件，过滤了不需要的部分
varfile = ''  # 变量文件，保存的主要数据，加快处理速度
one_picture = True  # 如果将所有曲线先是在一个图片中，one_picture = True ，反之，分散到各个图片中
time_intervial = 0.1  # 数据的时间间隔，单位：秒
plot_display = False  # 直接显示处理好的图片
cpu_list = []  # cpu数组，指定要处理的cpu
line_range = [0, 0]  # 设定范围，line_range[0]表示起始位置，line_range[1]表示终止位置
open_cmd = False  # 启用命令，允许进行实时处理
event_list = []  # 事件列表
fun_list = []  # 函数列表
picture_size = [20, 5]  # 图片大小

only_build_tmp = False
only_build_var = False

tracedatl = []  # tracedatl[0]为cpu数组，数组tracedatl[1]为采样时间的数组，tracedatl[2]为对应的事件
timesec = []  # 图片x轴的刻度数据
events = []  # 当前处理的数据包含的全部事件名
events_ascii = []  # 当前处理的数据包含的全部事件名，ascii格式
use_events_filter_i = []  # 在events_ascii中用event_list过滤出的下标数组
stats_array = []  # 处理好的统计数据
allcpu_stats_array = []  # 所有cpu的合并结果
cpu_number = 0

cur_line_data = []  # 当前需要展示曲线数据，cpu_line_data[x]表示一条曲线


def save_var(data, var_file):  # 保存数据
    try:
        with open(var_file, 'wb') as varfout:
            for i in data:
                pickle.dump(i, varfout)
    except OSError as file_open_error:
        print(file_open_error)
        print('打开文件：\''+var_file+'\'失败')
        return False
    return True


def readvar(var_file):  # 读取数据
    print("读取数据中。。。")
    try:
        with open(var_file, 'rb') as fin:
            tracedatl = pickle.load(fin)
            cpu_number = pickle.load(fin)
    except OSError as error1:
        print(error1)
        print('打开文件：\''+var_file+'\'失败')
        exit(1)
    return tracedatl, cpu_number


def statistical_data():  # 统计数据
    # 创建一个二维数组，用于记录每个函数在每秒的执行次数
    stats_array = np.zeros(
        [np.max(tracedatl[0])+1, len(events), len(timesec)], dtype=int, order='C')
    # 统计每个函数在每秒出现的时间，并置入funnamenum
    # x表示行，y表示列
    x, y, item = 0, 1, 0
    tmp1 = int(len(tracedatl[1])/100)
    for i in tracedatl[1]:
        if i > timesec[y]:
            y += 1
        # 逐个判断函数名
        x = 0
        for name in events:
            if name == tracedatl[2][item]:
                # 找到文件名，令其在funnamenum数组中对应的值加一
                stats_array[tracedatl[0][item]][x][y] += 1
                break
            x += 1
        item += 1
        if item % tmp1 == 0:
            process_bar(item/tmp1/100, start_str='',
                        end_str='100%', total_length=60)
    print()
    return stats_array

# 过滤指定数组，返回一个数组，长度与main_array相等，每个元素表示对应main_array元素在filter_array中的位置


def filter_array(main_array, filter_array):
    range_main = len(main_array)
    range_filter = len(filter_array)
    ret_array = np.zeros((range_filter), dtype=int, order='C')
    for i in range(range_main):
        for j in range(range_filter):
            if main_array[i] == filter_array[j]:
                ret_array[j] = i
                break
    return ret_array


cur_figure = plt.figure(figsize=picture_size)  # 当前绘图使用的平台
cur_ax = plt.gca()  # 当前axes对象


def setting_picture_x(value):
    # 更新刻度
    cur_ax.xaxis.set_major_locator(MultipleLocator(value))


def add_plt_line(x_axis, y_axis, label_name):  # 为当前figure增加曲线
    plt.plot(x_axis, y_axis, label=label_name)


def update_plt_figure(x_axis, y_axis, label_name, title_name):  # 更新当前figure的内容，会将之前的内容清除
    plt.title(title_name)
    plt.cla()
    plt.plot(x_axis, y_axis, label=label_name)
    plt.legend()


def create_picture(x_axis, y_axis, events_i, events_name, title):  # 创建图片
    plt.title(title)
    for i in events_i:
        plt.plot(x_axis[line_range[0]:line_range[1]], y_axis[i]
                 [line_range[0]:line_range[1]], label=events_name[i])
    plt.legend()


def save_picture(outfile):  # 保存图片
    outfile += '.jpg'
    plt.savefig(outfile)
    print('图片保存至\''+outfile+'\'')


def show_picture():  # 展示最新的figure
    plt.show()


'''
def save_show_picture(linedata, timesec, outputfile, events_ascii, use_events_filter_i, line_range, time_intervial=1, one_picture=True, plot_display=False, picture_size=[20, 5]):
    if one_picture:  # 将所有函数曲线放到一起
        plt.figure(figsize=picture_size)
        for i in use_events_filter_i:
            plt.plot(timesec[line_range[0]:line_range[1]],
                     linedata[i][line_range[0]:line_range[1]], label=events_ascii[i])
            plt.legend()
        outputfile += '.jpg'
        plt.savefig(outputfile)
        print('图片保存至\''+outputfile+'\'')
    else:  # 根据函数/事件名将曲线分为多个图片
        for i in use_events_filter_i:
            plt.figure(figsize=picture_size)
            plt.title(events_ascii[i])
            plt.plot(timesec[line_range[0]:line_range[1]],
                     linedata[i][line_range[0]:line_range[1]], label=events_ascii[i])
            picture1 = outputfile+'-'+events_ascii[i]+'.jpg'
            plt.savefig(picture1)
            print('图片保存至\''+picture1+'\'')
    # 设置刻度
    cur_ax = plt.gca() 
    cur_ax.xaxis.set_major_locator(MultipleLocator(time_intervial))
    # 展示图片
    if plot_display:
        plt.show()
    plt.clf()
    plt.close()
'''


parameter_cmd = {'show_picture': ['show'],  # 显示图片
                 'show_timesec': ['timeax', 'ta'],  # 显示时间刻度数组
                 'show_event': ['events', 'e'],  # 显示事件列表
                 'show_status': ['status'],  # 显示统计结果
                 'clear': ['cle', 'clear'],  # 清空窗口
                 'help': ['help', 'h'],  # 显示帮助
                 'show_fun': ['fun', 'f'],  # 展示函数列表
                 'setting': ['set', 's'],  # 对一些变量进行设定
                 'show_values': ['values', 'v']  # 展示所有可以被修改的变量
                 }

values_defult = {  # 此字典用来保存默认值
    'cpu_list': [],
    'line_range': [],
    'event_list': [],
    'fun_list': [],
    'picture_size': [],
    'one_picture': [],
    'time_intervial': []
}

values_cmd = {  # 此字典用来保存可以设置的变量名
    'cpu_list': ['cpu_list'],
    'line_range': ['line_range'],
    'event_list': ['event_list'],
    'fun_list': ['fun_list'],
    'picture_size': ['picture_size'],
    'one_picture': ['one_picture'],
    'time_intervial': ['time_intervial']
}


def update_cmd_default():  # 每调用一次 update_cmd_default 都会保存当前值作为默认值
    global values_defult, cpu_list, line_range, event_list, fun_list, picture_size, one_picture, time_intervial
    # 保存指定变量的默认值，防止出错
    values_defult['cpu_list'] = cpu_list
    values_defult['line_range'] = line_range
    values_defult['event_list'] = event_list
    values_defult['fun_list'] = fun_list
    values_defult['picture_size'] = picture_size
    values_defult['one_picture'] = one_picture
    values_defult['time_intervial'] = time_intervial


def check_str_digit_array(numarray):
    # 检查narray的每一项是否为数字
    for i in numarray:
        if not i.isdigit():
            return False
    return True


def setting_value(mystrvararr):
    global cpu_list, line_range, picture_size, time_intervial
    # 对一些变量进行设置，mystrarr是一个字符串，需要转换为数组，mystrvar[0]必须为“set”，mystrvar[1]表示要设置的变量名
    # mystrvar[2]为设置的值
    if mystrvararr[0] != 'set':
        return
    mystrvar_number = mystrvararr[2:]
    if check_str_digit_array(mystrvar_number):  # 数组为数字字符串
        value = [int(i) for i in mystrvar_number]
        if mystrvararr[1] in values_cmd['cpu_list']:
            cpu_list = value
        elif mystrvararr[1] in values_cmd['line_range']:
            line_range = value
        elif mystrvararr[1] in values_cmd['picture_size']:
            picture_size = value
        elif mystrvararr[1] in values_cmd['time_intervial']:
            time_intervial = value[0]
    # 对变量值进行更新


def _cmd_1():
    is_error = False
    yn = input("\n是否进入命令(Y/n)：")
    if yn != '' and yn != 'y' and yn != 'Y':
        return
    print("===========================================================")
    my_string = input(">>")
    while my_string != 'q' and my_string != 'quit':
        if my_string == '\n':
            continue
        elif my_string in parameter_cmd['show_picture']:
            # 按照默认值展示图片
            count = 0
            # 绘制全部曲线数据
            for curve in allcpu_stats_array:
                plt.plot(timesec[line_range[0]:line_range[1]],
                         curve[line_range[0]:line_range[1]], label=event_list[count])
                plt.legend()
                count += 1
            # 打开图片
            x_major = MultipleLocator(time_intervial)
            ax = plt.gca()
            ax.xaxis.set_major_locator(x_major)
            plt.show()
            plt.clf()
        elif my_string in parameter_cmd['show_event']:
            # 打印所有事件名
            print(events)
        elif my_string in parameter_cmd['show_fun']:
            # 打印所有函数
            print()
        elif my_string in parameter_cmd['show_timesec']:
            # 打印时间轴
            print(timesec)
        elif my_string in parameter_cmd['clear']:
            # 清空屏幕
            os.system('clear')
        elif my_string in parameter_cmd['show_status']:
            # 显示数据
            print(stats_array)
        elif my_string in parameter_cmd['help']:
            # 显示帮助
            print(list(parameter_cmd.values()))
        elif my_string in parameter_cmd['show_values']:
            print()
        else:
            my_string_array = re.split('[\\s|,|=]', my_string)
            if len(my_string_array) < 2:
                is_error = True
            elif my_string_array[0] in parameter_cmd['setting']:
                # 设置变量
                setting_value(my_string_array)
            else:
                is_error = True
        if is_error:
            is_error = False
            print("命令不合法！")
        my_string = input(">>")


'''
def get_picture():
    if cpu_list == []:
        save_show_picture(allcpu_stats_array, timesec, outputfile, events_ascii, use_events_filter_i,
                          line_range, time_intervial, one_picture, plot_display)
    else:  # 按cpu_list数组生成
        for i in cpu_list:
            save_show_picture(stats_array[i], timesec, outputfile+'-'+str(
                i), events_ascii, use_events_filter_i, line_range, time_intervial, one_picture, plot_display)
'''


def update_allcpu_stats_array(my_stats_array, cpul):  # 更新all_stats_array数组
    retarray = sum([my_stats_array[i] for i in cpul])
    return retarray


def init_value():
    global events, cpu_list, events_ascii, event_list, use_events_filter_i, timesec, stats_array, allcpu_stats_array, line_range
    events = np.unique(tracedatl[2])
    events_ascii = [str(i, 'ascii') for i in events]
    if event_list == []:  # 用户未指定事件列表，那生成全部事件列表
        event_list = events_ascii
        use_events_filter_i = [i for i in range(len(event_list))]
    else:
        use_events_filter_i = filter_array(events_ascii, event_list)
    if cpu_list == []:  # 没有指定cpu,则使用全部cpu
        cpu_list = [i for i in range(cpu_number)]
    # 创建秒间隔数组
    timesec = [cutdec(i, 6) for i in np.linspace(cutdec(tracedatl[1][0], 2), cutdec(tracedatl[1][-1], 2)+2*time_intervial,
                                                 int((cutdec(tracedatl[1][-1], 2)-cutdec(tracedatl[1][0], 2)+2*time_intervial)/time_intervial)+1)]
    # 获取统计数组
    stats_array = statistical_data()
    # 将所有cpu上的统计结果相加，获得整个进程的结果
    #allcpu_stats_array = sum(stats_array)
    allcpu_stats_array = update_allcpu_stats_array(stats_array, cpu_list)
    # 保存数据
    print('保存var数据到\''+varfile+'\'')
    if not save_var([tracedatl, stats_array, cpu_number], varfile):
        return
    if line_range == [0, 0]:
        line_range = [1, len(timesec)-2]  # 两端的统计是不准确的，所以用line_range限制显示范围
    if one_picture:
        create_picture(timesec, allcpu_stats_array,
                       use_events_filter_i, events_ascii, inputfile)
    else:  # 图片按照函数名/事件名拆分
        count = 0
        for i in use_events_filter_i:
            update_plt_figure(timesec[line_range[0]:line_range[1]], allcpu_stats_array[i]
                              [line_range[0]:line_range[1]], events_ascii[i], inputfile)
            save_picture(outputfile+'-'+str(count))
            count += 1
    show_picture()
    if open_cmd:
        # 进入命令处理程序
        _cmd_1()


def dat2tmp(datfile, tmpfile):
    # 检查文件是否存在
    datfile_path = Path(datfile)
    if not datfile_path.is_file():
        print('文件\''+datfile+'\'不存在')
        exit(1)
    start = datetime.datetime.now()
    # 使用shell将trace-cmd采样的数据转换为可识别的格式
    print("生成临时文件中。。。")
    shell_script0 = 'trace-cmd report -i '+datfile+' | head -n1 >' + tmpfile
    shell_script1 = 'trace-cmd report -i '+datfile + \
        ' | awk \'match($0,/\\[(...)\\].+(....\\.......): (.+): .+/,a){printf(\"%s %s %s\\n\",a[1],a[2],a[3])}\' >> ' + tmpfile
    os.system(shell_script0)
    os.system(shell_script1)
    end = datetime.datetime.now()
    print("临时文件保存于\'"+tmpfile+'\' 花费时间' +
          str((end-start).total_seconds())+'秒')
    if only_build_tmp:
        exit(0)
    return tmpfile


'''
def shrink_data(tracedatl):  #缩小数据的体积
    #首先检索一遍
'''


def tmp2var(tmpfile, varfile):
    global cpu_number
    print("整理数据中。。。")
    try:
        with open(tmpfile, 'rb') as fin:
            # 读取第一行cpu数量
            str_tmp = re.findall(
                'cpu_list=(\\d*)', str(fin.readline(), 'ascii'))
            if str_tmp != []:
                cpu_number = int(str_tmp[0])
            tracedatl = list(
                zip(*([[int(i.split()[0]), float(i.split()[1]), i.split()[2]] for i in fin])))
            # with open(varfile, 'wb') as varfout:
            #    pickle.dump([tracedatl,cpu_number], varfout)
    except OSError as file_open_error:
        print("文件打开失败：")
        print(file_open_error)
        return None
    if only_build_var:
        return None
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
# -l ：对目标文件缩小体积
# -e : 指定统计事件，以“,”划分，若值为“all”，表示全部事件
# -g : 指定统计函数，以“,”划分，若值为“all”，表示全部函数
# --only-build-tmp ：仅生成tmp文件
# --only-build-var : 仅生成var文件
# --cmd ： 进入命令处理程序


main_options = 'ac:de:g:r:sht:i:o:S:v:'
main_options_name = ['all', 'cpu=', 'display', 'split', 'help', 'varfile', 'tmpfile=',
                     'ifile=', 'ofile=', 'Scale', 'only-build-tmp', 'only-build-var', 'cmd']


def main(argv):
    global inputfile, outputfile, tmpfile, varfile, one_picture, time_intervial, plot_display, cpu_list
    global line_range, open_cmd, fun_list, event_list, tracedatl, cpu_number
    global only_build_tmp, only_build_var
    try:
        opts, args = getopt.getopt(argv, main_options, main_options_name)
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
        elif opt in ("-v", "--varfile"):
            varfile = arg
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
            cpu_list = [int(i) for i in arg.split(',')]
        elif opt in ("-r", "--range"):
            line_range = [int(i) for i in arg.split(',')]
            if len(line_range) > 2:
                print("'-r'只能指定两个参数： -r 起始下标,结束下标")
                exit(5)
        elif opt in ("--only-build-tmp"):
            only_build_tmp = True
        elif opt in ("--only-build-var"):
            only_build_var = True
        elif opt in ("--cmd"):
            open_cmd = True
        elif opt in ("-g"):
            fun_list = [i for i in arg.split(',')]
        elif opt in ("-e"):
            event_list = [i for i in arg.split(',')]
    filename1 = ''
    if varfile == '':
        if tmpfile == '':
            if inputfile == '':
                print("未指定输入文件")
                exit(1)
            else:
                filename1 = os.path.splitext(inputfile)[0]
                tmpfile = filename1+'.tmp'
                varfile = filename1+'.var'
                tracedatl = tmp2var(dat2tmp(inputfile, tmpfile), varfile)
        else:
            filename1 = os.path.splitext(tmpfile)[0]
            varfile = filename1+'.var'
            tracedatl = tmp2var(tmpfile, varfile)
    if tracedatl == None:
        return
    if tracedatl == []:
        tracedatl, cpu_number = readvar(varfile)
    if filename1 == '':
        filename1 = os.path.splitext(varfile)[0]
    if outputfile == '':
        outputfile = filename1
    init_value()


if __name__ == '__main__':
    start = datetime.datetime.now()
    main(sys.argv[1:])
    end = datetime.datetime.now()
    print('时长'+str((end-start).total_seconds()))
