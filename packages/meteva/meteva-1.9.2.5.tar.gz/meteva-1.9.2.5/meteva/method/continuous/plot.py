import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import meteva
import numpy as np
import  math
from  matplotlib import  cm
from matplotlib.ticker import NullFormatter, FixedLocator
import copy
import pandas as pd
import datetime
import scipy.stats as st


def scatter_regress(ob, fo,member_list = None, rtype="linear",vmax = None,vmin = None, ncol = None,save_path=None,show = False,dpi = 300, title="散点回归图",
                    sup_fontsize = 10,width = None,height = None,ylabel ="观测"):
    '''
    绘制观测-预报散点图和线性回归曲线
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path:图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含散点图和线性回归图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''

    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min < 0):
        num_min -= 0.1 * dmm
    else:
        num_min -= 0.1 * dmm
        if num_min < 0:  # 如果开始全大于，则最低值扩展不超过0
            num_min = 0
    num_max += dmm * 0.1
    if vmax is not None:
        num_max = vmax
    if vmin is not None:
        num_min = vmin
    dmm = num_max - num_min


    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    if ncol is None:
        if sub_plot_num ==1:
            ncols = 1
        elif sub_plot_num %2 == 0:
            ncols = 2
        else:
            ncols = 3
    else:
        ncols = ncol

    nrows = math.ceil(new_Fo_shape[0] / ncols)

    if height is None:
        if nrows==1:
            if ncols <3:
                height_fig = 3.5
            else:
                height_fig = 2.5
        else:
            if ncols > nrows:
                height_fig = 6
            else:
                height_fig = 7
    else:
        height_fig = height

    height_suptitle = 0.4
    height_xticks_title = 0.1
    height_hspace = 0.6
    heidht_axis = (height_fig - height_suptitle - height_xticks_title - height_hspace * (nrows - 1)) / nrows
    width_axis = heidht_axis
    width_yticks = 0.1
    width_wspace = width_yticks * 5
    if width is None:
        width_fig = width_axis * ncols + width_wspace * (ncols - 1) + width_yticks
    else:
        width_fig = width

    grid_count = meteva.base.grid([num_min,num_max,(num_max-num_min)/100],[num_min,num_max,(num_max-num_min)/100])


    fig = plt.figure(figsize=(width_fig,height_fig),dpi = dpi)
    for line in range(new_Fo_shape[0]):
        ob = ob.flatten()
        fo = new_Fo[line,:].flatten()
        markersize = width_axis * heidht_axis / np.sqrt(ob.size)
        if markersize < 0.3:
            markersize = 0.3
        elif markersize > 20:
            markersize = 20

        plt.subplot(nrows, ncols, line + 1)
        df =pd.DataFrame({"lon":fo,"lat":ob})
        sta_xy = meteva.base.sta_data(df)
        sta_xy["time"] = datetime.datetime(2020,1,1,0)
        sta_xy["data0"] = 1
        grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy,grid = grid_count)
        sta_count = meteva.base.interp_gs_linear(grd_count,sta_xy)
        colors = sta_count["data0"]
        sort_index = colors.argsort()
        fo_s = fo[sort_index]
        ob_s = ob[sort_index]
        colors = colors[sort_index]
        #plt.scatter(fo_s, ob_s, c=colors,s = markersize,cmap="tab20c")

        try:
            plt.scatter(fo_s, ob_s, c=colors, s=markersize, cmap="turbo")
        except:
            plt.scatter(fo_s, ob_s, c=colors, s=markersize, cmap="rainbow")
        #plt.plot(fo, ob, '.', color='b', markersize=markersize)

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suptitle/height_fig,
                            hspace=height_hspace/heidht_axis,wspace=width_wspace/width_axis)
        if rtype == "rate":
            ob_line = np.arange(num_min, num_max, dmm / 30)
            rate = np.mean(ob) / np.mean(fo)
            fo_rg = ob_line * np.mean(ob) / np.mean(fo)
            plt.plot(ob_line, fo_rg, color="k")
            rg_text2 = "Y = " + '%.2f' % rate + "X"
            plt.text(num_min + 0.05 * dmm, num_min + 0.92 * dmm, rg_text2, fontsize=0.8 * sup_fontsize, color="r")
        elif rtype == "linear":
            #X = np.zeros((len(fo), 1))
            #X[:, 0] = fo
            #clf = LinearRegression().fit(X, ob)
            # 斜率，截距，r 值，p 值，标准误差
            slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
            ob_line = np.arange(num_min, num_max, dmm / 30)
            # X = np.zeros((len(ob_line), 1))
            # X[:, 0] = ob_line
            #fo_rg = clf.predict(X)
            fo_rg = slope * ob_line + intercept
            plt.plot(ob_line, fo_rg, color="k")
            #rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
            if intercept >=0:
                rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
            else:
                rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

            plt.text(num_min + 0.05 * dmm, num_min + 0.92 * dmm, rg_text2, fontsize=0.8 * sup_fontsize, color="r")
        corr1 = meteva.method.corr(ob,fo)
        re_text1 = "corr = "+ '%.2f' % (corr1)
        plt.text(num_min + 0.05 * dmm, num_min + 0.85 * dmm, re_text1, fontsize=0.8 * sup_fontsize, color="r")


        plt.plot(ob_line, ob_line, '--', color="k",linewidth = 0.5)
        plt.xlim(num_min, num_max)
        plt.ylim(num_min, num_max)
        plt.xticks(fontsize = 0.8 * sup_fontsize)
        plt.yticks(fontsize = 0.8 * sup_fontsize)


        if member_list is None:
            #plt.title('预报'+str(line+1),fontsize = 0.9 * fontsize_sup)
            plt.xlabel('预报'+str(line+1), fontsize=0.9 * sup_fontsize)
        else:
            #plt.title(member_list[line],fontsize = 0.9 * fontsize_sup)
            plt.xlabel(member_list[line], fontsize=0.9 * sup_fontsize)
        #plt.xlabel("预报", fontsize=0.9 * fontsize_sup)

        plt.ylabel(ylabel, fontsize=0.9 * sup_fontsize)
        plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
        plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内
        #plt.grid(linestyle='--', linewidth=0.5)
    titlelines = title.split("\n")
    fig.suptitle(title, fontsize=sup_fontsize, y=0.99+0.01 * len(titlelines))

    if save_path is None:
        show = True
    else:
        meteva.base.tool.path_tools.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()
    return None




def pdf_plot(ob, fo,member_list = None,vmax = None,vmin = None, save_path=None,  show = False,dpi = 300,title="频率匹配检验图",
             sup_fontsize = 10,width = None,height = None,yscale = None,grid = False,percent = [0,1]):
    '''
    sorted_ob_fo 将传入的两组数据先进行排序
    然后画出折线图
    ----------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含频率匹配映射关系图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    if width is None:
        width = 8
    if height is None:
        height = width * 0.45

    fig = plt.figure(figsize=(width, height),dpi = dpi)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    if vmax is not None:
        num_max = vmax
    if vmin is not None:
        num_min = vmin
    dmm = num_max - num_min
    ob= ob.flatten()
    start_index = int(ob.size * percent[0])
    end_index= int(ob.size * percent[1])

    ob_sorted = np.sort(ob.flatten())

    ob_sorted_smooth = ob_sorted
    ob_sorted_smooth[1:-1] = 0.5 * ob_sorted[1:-1] + 0.25 * (ob_sorted[0:-2] + ob_sorted[2:])
    ob_sorted_smooth = ob_sorted_smooth[start_index:end_index]
    ax = plt.subplot(1, 2, 1)
    y = np.arange(len(ob_sorted_smooth)) / (len(ob_sorted_smooth))
    plt.plot(ob_sorted_smooth, y, label="观测")

    dss = ob_sorted_smooth - ob_sorted_smooth[0]
    fnq =[(dss != 0).argmax()]

    for line in range(new_Fo_shape[0]):
        if member_list is None:
            if new_Fo_shape[0] == 1:
                label = '预报'
            else:
                label = '预报' + str(line + 1)
        else:
            label = member_list[line]
        fo_sorted = np.sort(new_Fo[line, :].flatten())
        fo_sorted_smooth = fo_sorted
        fo_sorted_smooth[1:-1] = 0.5 * fo_sorted[1:-1] + 0.25 * (fo_sorted[0:-2] + fo_sorted[2:])
        fo_sorted_smooth = fo_sorted_smooth[start_index:end_index]

        plt.plot(fo_sorted_smooth, y, label=label)
        plt.xlabel("变量值", fontsize=0.9 * sup_fontsize)
        #plt.xlim(num_min, num_max)

        plt.ylabel("累积概率", fontsize=0.9 * sup_fontsize)
        plt.title("概率分布函数对比图", fontsize=0.9 * sup_fontsize)
        yticks = np.arange(0, 1.01, 0.1)
        plt.yticks(yticks, fontsize=0.8 * sup_fontsize)
        plt.xticks(fontsize=0.8 * sup_fontsize)
        plt.legend(loc="lower right")
        if yscale =="log":
            ax.set_yscale('log')
            major_locator = [0.00001,0.0001,0.001,0.01,0.1,0.5]
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_major_locator(FixedLocator(major_locator))
            ax.set_yticklabels(major_locator)
        elif yscale == "logit":
            major_locator=[0.1,0.5,0.9,0.99,0.999,0.9999,0.99999]
            ax.set_yscale('logit')
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_major_locator(FixedLocator(major_locator))
            ax.set_yticklabels(major_locator)
            dss = fo_sorted_smooth - fo_sorted_smooth[0]
            fnq.append((dss!=0).argmax())

        else:
            plt.ylim(0, 1)

    if yscale == "logit":
        minfnq = min(fnq)/ob_sorted_smooth.size
        plt.ylim(minfnq,1)


        #plt.yscale('logit')
    if grid:
        plt.grid()

    plt.subplot(1, 2, 2)
    ob_line = np.arange(num_min, num_max, dmm / 30)
    plt.plot(ob_line, ob_line, '--')
    for line in range(new_Fo_shape[0]):
        if member_list is None:
            if new_Fo_shape[0] == 1:
                label = '预报'
            else:
                label = '预报' + str(line + 1)
        else:
            label = member_list[line]
        fo_sorted = np.sort(new_Fo[line, :].flatten())
        fo_sorted_smooth = fo_sorted
        fo_sorted_smooth[1:-1] = 0.5 * fo_sorted[1:-1] + 0.25 * (fo_sorted[0:-2] + fo_sorted[2:])
        fo_sorted_smooth = fo_sorted_smooth[start_index:end_index]
        plt.plot(fo_sorted_smooth, ob_sorted_smooth, linewidth=2, label=label)
        plt.xlim(num_min, num_max)
        plt.ylim(num_min, num_max)
        plt.xlabel("预报", fontsize=0.9 * sup_fontsize)
        plt.ylabel("观测", fontsize=0.9 * sup_fontsize)
        plt.title("频率匹配映射关系图", fontsize=0.9 * sup_fontsize)
        plt.legend(loc="lower right", fontsize=0.9 * sup_fontsize)
        plt.yticks(fontsize=0.8 * sup_fontsize)
        plt.xticks(fontsize=0.8 * sup_fontsize)
    if title is not None:
        plt.suptitle(title + "\n", y=1.00, fontsize=sup_fontsize)
    if grid:
        plt.grid()
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def box_plot_continue(ob, fo,  member_list=None,vmax = None,vmin = None, save_path=None, show = False,dpi = 300,title="频率对比箱须图",
                      sup_fontsize = 10,width = None,height = None,):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含箱须图，等级包括,横坐标为"观测"、"预报"，纵坐标为数据值
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    list_fo = list(new_Fo)

    xticks = ['观测']
    if member_list is None:
        if new_Fo_shape[0] == 1:
            xticks.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                xticks.append('预报' + str(i + 1))
    else:
        xticks.extend(member_list)

    #print(width)
    new_list_fo = []
    ob = ob.flatten()
    new_list_fo.append(ob)
    for fo_piece in list_fo:
        new_list_fo.append(fo_piece.flatten())

    tuple_of_ob = tuple(new_list_fo)
    if width is None:
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize) +0.5
        if width >10:
            for i in range(len(xticks)):
                if i % 2 ==1:
                    xticks[i] ="|\n" + xticks[i]
            width = 10
        elif width < 5:
            width = 5

    if height is None:
        height = width/2

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    markersize = 5 * width * height / np.sqrt(ob.size)
    if markersize < 1:
        markersize = 1
    elif markersize > 20:
        markersize = 20
    colors_list= []
    colors = cm.get_cmap('rainbow', 128)
    for i in range(len(xticks)):
        color_grade = i / len(xticks)
        colors_list.append(colors(color_grade))

    bplot = plt.boxplot(tuple_of_ob, showfliers=True, patch_artist=True, labels=xticks)


    plt.xticks(fontsize = 0.9 * sup_fontsize)
    plt.yticks(fontsize = 0.9 * sup_fontsize)

    plt.title(title,fontsize = sup_fontsize)
    for i, item in enumerate(bplot["boxes"]):
        item.set_facecolor(colors_list[i])
    #plt.title(title, fontsize=sup_fontsize)

    if vmin is not None or vmax is not None:
        if vmin is not None:
            if vmax is None:
                vmax = max(np.max(ob), np.max(fo))
                dmax = vmax - vmin
                plt.ylim(vmin,vmax+ dmax * 0.05)
            else:
                plt.ylim(vmin, vmax)
        else:
            vmin =  min(np.min(ob), np.min(fo))
            dmax = vmax - vmin
            plt.ylim(vmin- dmax * 0.05,vmax)


    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()



'''
def box_plot_continue(ob, fo,  member_list=None,vmax = None,vmin = None, save_path=None, show = False,dpi = 300,title="频率对比箱须图",
                      sup_fontsize = 10,width = None,height = None,):
    
    #box_plot 画一两组数据的箱型图
    #---------------
    #:param Ob: 实况数据  任意维numpy数组
    #:param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    #:param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    #:return:图片，包含箱须图，等级包括,横坐标为"观测"、"预报"，纵坐标为数据值
    
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    list_fo = list(new_Fo)

    xticks = ['观测']
    if member_list is None:
        if new_Fo_shape[0] == 1:
            xticks.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                xticks.append('预报' + str(i + 1))
    else:
        xticks.extend(member_list)

    #print(width)
    new_list_fo = []
    ob = ob.flatten()
    new_list_fo.append(ob)
    for fo_piece in list_fo:
        new_list_fo.append(fo_piece.flatten())

    tuple_of_ob = tuple(new_list_fo)
    if width is None:
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize) +0.5
        if width >10:
            for i in range(len(xticks)):
                if i % 2 ==1:
                    xticks[i] ="|\n" + xticks[i]
            width = 10
        elif width < 5:
            width = 5

    if height is None:
        height = width/2

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    markersize = 5 * width * height / np.sqrt(ob.size)
    if markersize < 1:
        markersize = 1
    elif markersize > 20:
        markersize = 20
    colors_list= []
    colors = cm.get_cmap('rainbow', 128)
    for i in range(len(xticks)):
        color_grade = i / len(xticks)
        colors_list.append(colors(color_grade))

    bplot = plt.boxplot(tuple_of_ob, showfliers=True, patch_artist=True, labels=xticks)


    plt.xticks(fontsize = 0.9 * sup_fontsize)
    plt.yticks(fontsize = 0.9 * sup_fontsize)

    plt.title(title,fontsize = sup_fontsize)
    for i, item in enumerate(bplot["boxes"]):
        item.set_facecolor(colors_list[i])
    #plt.title(title, fontsize=sup_fontsize)

    if vmin is not None or vmax is not None:
        if vmin is not None:
            if vmax is None:
                vmax = max(np.max(ob), np.max(fo))
                dmax = vmax - vmin
                plt.ylim(vmin,vmax+ dmax * 0.05)
            else:
                plt.ylim(vmin, vmax)
        else:
            vmin =  min(np.min(ob), np.min(fo))
            dmax = vmax - vmin
            plt.ylim(vmin- dmax * 0.05,vmax)


    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()

'''


def taylor_diagram(ob, fo,member_list=None, save_path=None,show = False,dpi = 300, title="",
                sup_fontsize =10,width = None,height = None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''

    leftw = 0.3
    rightw = 1.5
    uphight = 1.2
    lowhight = 1.2
    axis_size_x = 3
    axis_size_y = 3
    if width is None:
        width = axis_size_x + leftw + rightw

    if height is None:
        height = axis_size_y + uphight + lowhight

    stds = meteva.method.ob_fo_std(ob,fo)
    corrs = meteva.method.corr(ob,fo)
    corrs1 = [1]
    if isinstance(corrs,float):
        corrs1.append(corrs)
    else:
        for i in range(len(corrs)):
            corrs1.append(corrs[i])


    fig = plt.figure(figsize=(width, height),dpi=dpi)
    ax1 = fig.add_axes([leftw / width, lowhight / width, axis_size_x / width, axis_size_y / height])


    max_stds = max(stds)

    dif = (max_stds) / 10.0
    if dif == 0:
        inte = 1
    else:
        inte = math.pow(10, math.floor(math.log10(dif)))
    # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
    r = dif / inte

    if r < 2.3:
        inte = inte * 2
    elif r < 7:
        inte = inte * 5
    else:
        inte = inte * 10
    vmax = inte * ((int)(max_stds / inte) + 1)

    std_list = np.arange(inte,vmax+inte/2,inte)

    corr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,0.98]
    #画观测弧线
    # 画弧线
    angle = np.arange(0,math.pi/2,math.pi/1000)
    std = stds[0]
    x2 = np.cos(angle) * std
    y2 = np.sin(angle) * std
    plt.plot(x2, y2,color = "steelblue",linewidth = 1)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std
        y2 = np.sin(angle) * std
        if i <len(std_list)-1:
            plt.plot(x2, y2, ":", color="k", linewidth=0.5)
        else:
            plt.plot(x2, y2,color = "k",linewidth = 0.5)


    #画围绕观测的弧线
    angle = np.arange(0,math.pi,math.pi/1000)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std + stds[0]
        y2 = np.sin(angle) * std
        dis = np.sqrt(x2 * x2 + y2 * y2)
        x2 = x2[dis < vmax]
        y2 = y2[dis < vmax]

        plt.plot(x2, y2, ":", color="g", linewidth=0.5)

    #相关系数射线
    r0 = np.arange(0,vmax,inte/100)
    for i in range(len(corr_list)):
        corr = corr_list[i]
        angle = np.arccos(corr)
        x1 = r0 * np.cos(angle)
        y1 = r0 * np.sin(angle)
        ax1.plot(x1, y1, '-.', color='b', linewidth=0.4)
        rt = vmax* 1.01
        xt = rt * np.cos(angle)
        yt = rt * np.sin(angle)
        ax1.text(xt, yt, str(corr),fontsize = sup_fontsize * 0.8)


    angle = 60 * math.pi/180
    rt = vmax * 1.01
    xt = rt * np.cos(angle)
    yt = rt * np.sin(angle)

    ax1.text(xt, yt,"相关系数" , fontsize=sup_fontsize * 0.8,rotation=-30,)

    ax1.set_xticks(std_list)
    ax1.set_yticks(std_list)
    ax1.set_xlim(0,vmax)
    ax1.set_ylim(0, vmax)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.set_xlabel("标准差")
    ax1.set_ylabel("标准差")



    # 画预报观测点
    labels = ["观测"]
    labels.extend(member_list)
    for i in range(len(stds)):
        corr = corrs1[i]
        angle = np.arccos(corr)
        xp = stds[i] * np.cos(angle)
        yp = stds[i] * np.sin(angle)
        ax1.plot(xp, yp,"o", label=labels[i], markersize=6)
    lines, label1 = ax1.get_legend_handles_labels()

    if len(stds)> 7:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.4, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    elif len(stds)>5:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.2, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    else:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.1, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    ax1.add_artist(legend2)


    title = title + "\n"
    ax1.set_title(title,fontsize = sup_fontsize)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def taylor_diagram_(ob, fo,member_list=None, save_path=None,show = False,dpi = 300, title="",
                sup_fontsize =10,width = None,height = None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''

    leftw = 0.3
    rightw = 1.5
    uphight = 1.2
    lowhight = 1.2
    axis_size_x = 3
    axis_size_y = 3
    if width is None:
        width = axis_size_x + leftw + rightw

    if height is None:
        height = axis_size_y + uphight + lowhight

    stds = meteva.method.ob_fo_std(ob,fo)
    corrs = meteva.method.corr(ob,fo)
    corrs1 = [1]
    if isinstance(corrs,float):
        corrs1.append(corrs)
    else:
        for i in range(len(corrs)):
            corrs1.append(corrs[i])


    fig = plt.figure(figsize=(width, height),dpi=dpi)
    ax1 = fig.add_axes([leftw / width, lowhight / width, axis_size_x / width, axis_size_y / height])


    max_stds = max(stds)

    dif = (max_stds) / 10.0
    if dif == 0:
        inte = 1
    else:
        inte = math.pow(10, math.floor(math.log10(dif)))
    # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
    r = dif / inte

    if r < 2.3:
        inte = inte * 2
    elif r < 7:
        inte = inte * 5
    else:
        inte = inte * 10
    vmax = inte * ((int)(max_stds / inte) + 1)

    std_list = np.arange(inte,vmax+inte/2,inte)

    corr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,0.98]
    #画观测弧线
    # 画弧线
    angle = np.arange(0,math.pi/2,math.pi/1000)
    std = stds[0]
    x2 = np.cos(angle) * std
    y2 = np.sin(angle) * std
    plt.plot(x2, y2,color = "steelblue",linewidth = 1)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std
        y2 = np.sin(angle) * std
        if i <len(std_list)-1:
            plt.plot(x2, y2, ":", color="k", linewidth=0.5)
        else:
            plt.plot(x2, y2,color = "k",linewidth = 0.5)


    #画围绕观测的弧线
    angle = np.arange(0,math.pi,math.pi/1000)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std + stds[0]
        y2 = np.sin(angle) * std
        dis = np.sqrt(x2 * x2 + y2 * y2)
        x2 = x2[dis < vmax]
        y2 = y2[dis < vmax]

        plt.plot(x2, y2, ":", color="g", linewidth=0.5)

    #相关系数射线
    r0 = np.arange(0,vmax,inte/100)
    for i in range(len(corr_list)):
        corr = corr_list[i]
        angle = np.arccos(corr)
        x1 = r0 * np.cos(angle)
        y1 = r0 * np.sin(angle)
        ax1.plot(x1, y1, '-.', color='b', linewidth=0.4)
        rt = vmax* 1.01
        xt = rt * np.cos(angle)
        yt = rt * np.sin(angle)
        ax1.text(xt, yt, str(corr),fontsize = sup_fontsize * 0.8)


    angle = 60 * math.pi/180
    rt = vmax * 1.01
    xt = rt * np.cos(angle)
    yt = rt * np.sin(angle)

    ax1.text(xt, yt,"相关系数" , fontsize=sup_fontsize * 0.8,rotation=-30,)

    ax1.set_xticks(std_list)
    ax1.set_yticks(std_list)
    ax1.set_xlim(0,vmax)
    ax1.set_ylim(0, vmax)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.set_xlabel("标准差")
    ax1.set_ylabel("标准差")



    # 画预报观测点
    labels = ["观测"]
    labels.extend(member_list)
    for i in range(len(stds)):
        corr = corrs1[i]
        angle = np.arccos(corr)
        xp = stds[i] * np.cos(angle)
        yp = stds[i] * np.sin(angle)
        ax1.plot(xp, yp,"o", label=labels[i], markersize=6)
    lines, label1 = ax1.get_legend_handles_labels()

    if len(stds)> 7:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.4, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    elif len(stds)>5:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.2, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    else:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.1, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    ax1.add_artist(legend2)


    title = title + "\n"
    ax1.set_title(title,fontsize = sup_fontsize)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()



def frequency_histogram_error(ob, fo,grade_list=None, member_list=None,  vmax = None,save_path=None,show = False,dpi = 300,plot = "bar", title="误差频率统计图",
                        sup_fontsize = 10,width = None,height = None,log_y = False,color_list = None,linestyle = None):
    '''
    frequency_histogram 对比测试数据和实况数据的发生的频率
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :param save_path: 保存地址
    :return: 无
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape


    legend = []
    if member_list is None:
        if new_Fo_shape[0] <= 1:
            legend.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                legend.append('预报' + str(i + 1))
    else:
        legend.extend(member_list)

    error = new_Fo - ob

    result_array = meteva.method.frequency_table(ob, error, grade_list=grade_list)
    result_array = result_array[1:,:]

    total_count = np.sum(result_array[0,:])
    result_array /= total_count
    if grade_list is not None:
        if len(grade_list) >10:
            axis = ["<\n" + str(round(grade_list[0],6))]
            for index in range(len(grade_list)):
                axis.append(str(round(grade_list[index],6)))
            axis.append(">=\n" + str(round(grade_list[-1],6)))
        else:
            axis = ["<" + str(round(grade_list[0],6))]
            for index in range(len(grade_list) - 1):
                axis.append("[" + str(round(grade_list[index],6)) + "," + str(round(grade_list[index + 1],6)) + ")")
            axis.append(">=" + str(round(grade_list[-1],6)))


    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        fo_list = list(set(new_fo.tolist()))
        fo_list.extend(list(set(new_ob.tolist())))
        axis = list(set(fo_list))

    name_list_dict = {}
    name_list_dict["legend"] = legend
    name_list_dict["类别"] = axis
    if log_y:
        vmin = None
    else:
        vmin = 0
    if plot == "bar":
        meteva.base.plot_tools.bar(result_array,name_list_dict,ylabel= "样本占比",vmin = vmin,vmax = vmax,save_path = save_path,show = show,dpi = dpi,title=title,
                                   width = width,height = height,sup_fontsize= sup_fontsize,log_y = log_y,color_list=color_list)
    else:
        meteva.base.plot_tools.plot(result_array, name_list_dict, ylabel="样本占比", vmin=vmin, vmax=vmax, save_path=save_path,
                                   show=show, dpi=dpi, title=title,
                                    width = width,height = height,sup_fontsize= sup_fontsize,log_y = log_y,color_list=color_list,linestyle=linestyle)



def accumulation_change_with_strength(ob,fo,member_list = None,save_path=None,  show = False,dpi = 300,title="降水量随强度变化图",
             sup_fontsize = 14,width = None,height = None,log_y = False,y_log = None,max_x = None):
    if y_log is not None:
        print(
            "warning: the argument y_log will be abolished, please use log_y instead\n警告：为保持和其它函数的名称一致，参数log_y将被废除，以后请使用参数log_y代替")
        log_y = y_log

    accu_stren = meteva.method.continuous.table.accumulation_strength_table(ob,fo)
    min_not_zero = np.min(accu_stren[accu_stren>0])
    maxv = np.max(accu_stren)
    shape = accu_stren.shape
    grade = np.arange(1,shape[1]+1,1)
    nfo = shape[0]-1
    if width is None:
        width = 10
    if height is None:
        height = width *0.6

    fig = plt.figure(figsize=(width, height),dpi = dpi)

    if member_list is None:
        labels = ["观测"]
        for i in range(1,nfo+1):
            labels.append("预报"+str(i))
    else:
        labels = ["观测"]
        labels.extend(member_list)
    for line in range(len(labels)):
        plt.plot(grade,accu_stren[line], label=labels[line],marker = ".")
        plt.xlabel("降水强度(毫米/小时)", fontsize=0.9 * sup_fontsize)
        plt.ylabel("累计降水量", fontsize=0.9 * sup_fontsize)
        plt.title(title, fontsize=0.9 * sup_fontsize)
        if(log_y):
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        plt.xticks(fontsize=0.8 * sup_fontsize)
        plt.legend(loc="upper right")



    # 设置次刻度间隔
    if max_x is not None:
        maxx = max_x
    else:
        maxx = len(grade)
    if(maxx <20):
        xmi = 1
        Xmi = 1
    elif(maxx <50):
        xmi = 1
        Xmi = 5
    elif (maxx <100):
        xmi = 1
        Xmi = 10
    elif (maxx <300):
        xmi = 5
        Xmi = 20
    elif (maxx <1000):
        xmi = 10
        Xmi = 50
    else:
        xmi = 50
        Xmi = 200
    ax1 = plt.gca()
    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ax1.xaxis.set_major_locator(xmajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    ax1.xaxis.set_minor_locator(xminorLocator)
    plt.xlim(0,maxx)
    if log_y:
        plt.ylim(min_not_zero,maxv * 3)
    else:
        plt.ylim(0,maxv * 1.1)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path, bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()
    return accu_stren

def frequency_change_with_strength(ob,fo,member_list = None,save_path=None,  show = False,dpi = 300,title="降水频次随强度变化图",
             sup_fontsize = 14,width = None,height = None,log_y = False,y_log = None,max_x = None,color_list = None,linestyle = None,smooth = None):

    if y_log is not None:
        print(
            "warning: the argument y_log will be abolished, please use log_y instead\n警告：为保持和其它函数的名称一致，参数log_y将被废除，以后请使用参数log_y代替")
        log_y = y_log

    accu_stren = meteva.method.continuous.table.frequency_strength_table(ob,fo)
    if smooth is not None:
        for i in range(accu_stren.shape[0]):
            accu_stren1 = accu_stren[i,:]
            accu_stren_sm = accu_stren[i,:]
            for k in range(smooth):
                accu_stren_sm[10:-1] = 0.25 * accu_stren1[11:] + 0.25 * accu_stren1[9:-2] + 0.5 * accu_stren1[10:-1]
                accu_stren1[:] = accu_stren_sm[:]
            accu_stren[i, :]  = accu_stren_sm[:]

    min_not_zero = np.min(accu_stren[accu_stren>=1])
    maxv = np.max(accu_stren)
    shape = accu_stren.shape
    grade = np.arange(1,shape[1]+1,1)
    nfo = shape[0]-1
    if width is None:
        width = 10
    if height is None:
        height = width *0.6

    fig = plt.figure(figsize=(width, height),dpi = dpi)

    if member_list is None:
        labels = ["观测"]
        for i in range(1,nfo+1):
            labels.append("预报"+str(i))
    else:
        if len(member_list) == shape[0]:
            labels = member_list
        else:
            labels = ["观测"]
            labels.extend(member_list)

    for line in range(len(labels)):
        if linestyle is None:
            style = "-"
        else:
            style = linestyle[line]
        if color_list is None:
            plt.plot(grade,accu_stren[line], label=labels[line],marker = ".",linestyle=style)
        else:
            plt.plot(grade, accu_stren[line], label=labels[line], marker=".",color = color_list[line],linestyle = style)

    plt.xlabel("降水强度(毫米/小时)", fontsize=0.9 * sup_fontsize)
    plt.ylabel("降水频次", fontsize=0.9 * sup_fontsize)
    plt.title(title, fontsize=0.9 * sup_fontsize)
    if(log_y):
        ax_one = plt.gca()
        for tick in ax_one.yaxis.get_major_ticks():
            tick.label1.set_fontproperties('stixgeneral')
        plt.yscale('log')
    plt.xticks(fontsize=0.8 * sup_fontsize)
    plt.legend(loc="upper right")




    # 设置次刻度间隔
    if max_x is not None:
        maxx = max_x
    else:
        maxx = len(grade)
    if(maxx <20):
        xmi = 1
        Xmi = 1
    elif(maxx <50):
        xmi = 1
        Xmi = 5
    elif (maxx <100):
        xmi = 1
        Xmi = 10
    elif (maxx <300):
        xmi = 5
        Xmi = 20
    elif (maxx <1000):
        xmi = 10
        Xmi = 50
    else:
        xmi = 50
        Xmi = 200
    ax1 = plt.gca()
    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ax1.xaxis.set_major_locator(xmajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    ax1.xaxis.set_minor_locator(xminorLocator)
    plt.xlim(0,maxx)
    if log_y:
        plt.ylim(min_not_zero,maxv * 3)
    else:
        plt.ylim(0,maxv * 1.1)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path, bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()
    return accu_stren



def accumulation_change_with_strenght(ob,fo,member_list = None,save_path=None,  show = False,dpi = 300,title="降水量随强度变化图",
             sup_fontsize = 14,width = None,height = None,log_y = False,y_log = None,max_x = None):
    return accumulation_change_with_strength(ob,fo,member_list=member_list,save_path=save_path,show=show,dpi=dpi,title=title,
                                      sup_fontsize=sup_fontsize,width = width,height=height,log_y=log_y,y_log=y_log,max_x=max_x)

def frequency_change_with_strenght(ob,fo,member_list = None,save_path=None,  show = False,dpi = 300,title="降水频次随强度变化图",
             sup_fontsize = 14,width = None,height = None,log_y = False,y_log = None,max_x = None,color_list = None,linestyle = None,smooth = None):
    return  frequency_change_with_strength(ob,fo,member_list=member_list,save_path=save_path,show=show,dpi=dpi,title=title,sup_fontsize=sup_fontsize,width=width,height=height,
                                   log_y=log_y,y_log=y_log,max_x=max_x,color_list=color_list,linestyle=linestyle,smooth=smooth)