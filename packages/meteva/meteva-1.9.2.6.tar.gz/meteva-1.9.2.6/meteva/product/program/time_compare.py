import numpy as np
import matplotlib.pyplot as plt
import datetime
import meteva
import matplotlib.patches as patches
import math
import pandas as pd
import json


def time_list_line_error(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,show = False,dpi = 300,title = "多时效预报误差对比图",
                         sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    sta_ob_and_fos1 = meteva.base.sele_by_para(sta_ob_and_fos1,drop_IV=True)

    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    ids.sort()
    nids = len(ids)

    if isinstance(title, list):
        if nids != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    if json_path is not None:
        if isinstance(json_path,str):
            json_path = [json_path]
        if nids != len(json_path):
            print("手动设置的json_path数目和要绘制的图形数目不一致")
            return

    for n in range(nids):
        id = ids[n]
        sta_ob_and_fos = meteva.base.in_id_list(sta_ob_and_fos1,[id])
        times_fo = sta_ob_and_fos.loc[:, "time"].values
        times_fo = list(set(times_fo))
        # print(times_fo)
        if (len(times_fo) == 1):
            print("仅有单个起报时间的预报，程序退出")
            return
        times_fo.sort()
        times_fo = np.array(times_fo)
        dhs_fo = (times_fo[1:] - times_fo[0:-1])
        if isinstance(dhs_fo[0], np.timedelta64):
            dhs_fo = dhs_fo / np.timedelta64(1, 'h')
        else:
            dhs_fo = dhs_fo / datetime.timedelta(hours=1)
        dhs_fo_not0 = dhs_fo[dhs_fo != 0]
        dh_y = np.min(dhs_fo_not0)

        dhs = list(set(sta_ob_and_fos.loc[:, "dtime"].values))
        dhs.sort()
        dhs = np.array(dhs)
        # 以观预报时效间隔的最小单位
        ddhs = dhs[1:] - dhs[0:-1]
        dh_x = int(np.min(ddhs))

        if width is None:
            width = len(dhs) * 1.2
            if width > 8:width = 8
        if height is None:
            height = len(times_fo) * 1.0
            if height > 5:height = 5

        fig = plt.figure(figsize=(width, height),dpi = dpi)
        grid_plt = plt.GridSpec(len(times_fo), 1, hspace=0)

        time_f0 = times_fo[0]
        data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
        error_array = np.zeros((len(sta_ob_and_fos.index),len(data_names)-1))
        for i in range(len(data_names)-1):
            error_array[:,i] = sta_ob_and_fos.values[:, 7+i] - sta_ob_and_fos.values[:, 6]
        vmax0 = np.max(error_array)
        vmin0 = np.min(error_array) - 0.1
        maxerr = np.maximum(vmax0,-vmin0)
        vmax = maxerr * 1.05
        vmin = -maxerr * 1.05
        #vmax = (vmax - vmin) * 1.2 + vmin
        dif = (vmax - vmin)/2
        inte = math.pow(10, math.floor(math.log10(dif)))
        # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
        r = dif / inte
        if(r<1.5):
            inte = inte * 0.5
        elif r < 3 and r >= 1.5:
            inte = inte * 1
        elif r < 4.5 and r >= 3:
            inte = inte * 2
        elif r < 5.5 and r >= 4.5:
            inte = inte * 3
        elif r < 7 and r >= 5.5:
            inte = inte * 3
        elif r >= 7:
            inte = inte * 4
        yticks = np.array([-inte,0,inte])

        dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
        obtimes = sta_ob_and_fos['time'] + dtimes
        #obtimes[-1] = times_fo[0]
        time_all = list(set(obtimes))
        time_all.sort()
        #print(time_all)
        dtime_all = pd.Series(time_all) - times_fo[0]
        x_all = dtime_all/np.timedelta64(1, 'h')
        x_all = x_all.values
        x_plot, time_strs = meteva.product.program.get_x_ticks(time_all, width-1)
        x_plot += x_all[0]

        time_strs_null = []
        for i in range(len(time_strs)):
            time_strs_null.append("")

        all_y_label = []

        picture_ele_dict = {}
        picture_ele_dict["xticklabels"] = meteva.product.program.fun.get_time_str_list(time_all,row=3)
        picture_ele_dict["vmin"] = vmin
        picture_ele_dict["vmax"] = vmax
        picture_ele_dict["subplots"] ={}

        for i in range(len(times_fo)):
            ax = plt.subplot(grid_plt[i:i + 1, 0])
            picture_ele_dict["subplots"][i] = {}
            time_f1 = times_fo[-i - 1]
            dhour0 = (time_f1 - time_f0) / np.timedelta64(1, 'h')
            sta = meteva.base.in_time_list(sta_ob_and_fos, [time_f1])
            sta = sta.sort_values("dtime")
            x = dhour0 + sta.loc[:, "dtime"].values
            plt.plot(x,np.zeros(x.size),linewidth = sup_fontsize *0.07)
            for name in data_names[1:]:
                value = sta.loc[:, name].values - sta.iloc[:, 6].values
                #plt.plot(x, value, label=name,marker = ".",linewidth = sup_fontsize *0.1,markersize = sup_fontsize *0.3)

                #value = sta.loc[:, name].values
                index_iv = np.where(value == meteva.base.IV)
                dat0_all = meteva.base.tool.plot_tools.set_plot_IV_with_out_start_end(value)
                plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                x_iv = x[index_iv[0]]
                dat0_iv = dat0_all[index_iv[0]]
                plt.plot(x_iv, dat0_iv, ".", color='k',markersize = sup_fontsize * 0.1)
                dat0_notiv = value.copy()
                dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                plt.plot(x, dat0_notiv, label=name,marker = ".",linewidth = sup_fontsize * 0.1,markersize = sup_fontsize * 0.3)

                plt.ylim(vmin, vmax)
                plt.yticks(yticks,fontsize = sup_fontsize *0.6)
                plt.xlim(x_all[0],x_all[-1])
                plt.grid(linestyle='-.',linewidth = sup_fontsize *0.07)

                picture_ele_dict["subplots"][i][name] = {}
                picture_ele_dict["subplots"][i][name]["x"] = x.tolist()
                picture_ele_dict["subplots"][i][name]["value"] = value.tolist()


            time_f1 = meteva.base.tool.time_tools.all_type_time_to_datetime(time_f1)
            time_str = time_f1.strftime('%d{d}%H{h}').format(d='日', h='时')+"        "
            all_y_label.append(time_str)
            plt.ylabel(time_str, rotation='horizontal',fontsize = sup_fontsize * 0.75)
            if i ==0:
                plt.legend(loc="upper left", ncol=len(data_names),fontsize = sup_fontsize * 0.9)
                s1 = s
                if s1 is None:
                    s1 = {}
                    s1["id"] = id

                if isinstance(title,list):
                    title1 = title[n]
                else:
                    title1 = meteva.product.program.get_title_from_dict(title, s1, None, None,
                                                                    None)

                    title1 = title1.replace("\n","")
                plt.title(title1,fontsize = sup_fontsize)
                picture_ele_dict["title"] = title1

            #plt.hlines(0,x_plot[0],x_plot[-1],"k",linewidth = 0.5)
            if i == len(times_fo) - 1:
                plt.xticks(x_plot, time_strs,fontsize =  sup_fontsize * 0.8)
                if meteva.base.language=="ch":
                    plt.xlabel("实况时间",fontsize = sup_fontsize * 0.9)
                else:
                    plt.xlabel("observation time", fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks(x_plot,time_strs_null)

        picture_ele_dict["y_label"] = all_y_label

        rect_ylabel = [0.03, 0.45, 0.0, 0.0]  # 左下宽高
        ax_ylabel = plt.axes(rect_ylabel)
        ax_ylabel.axes.set_axis_off()
        if meteva.base.language=="ch":
            plt.text(0, 0, "起报时间", fontsize=sup_fontsize * 0.9, rotation=90)
        else:
            plt.text(0, 0, "time", fontsize=sup_fontsize * 0.9, rotation=90)
        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir+"/" + str(id) + ".png"
        else:
            save_path1 = save_path[n]

        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            if meteva.base.language:
                print("图片已保存至" + save_path1)
            else:
                print("fig has saved to ")
        if show:
            plt.show()
        plt.close()


        json_path1 = None
        if json_path is None:
            if json_dir is None:
                pass
            else:
                json_path1 = json_dir+"/" + str(id) + ".json"
        else:
            json_path1 = json_path[n]

        if json_path1 is not None:
            meteva.base.tool.path_tools.creat_path(json_path1)
            file = open(json_path1,"w")
            json.dump(picture_ele_dict,file)
            print("have printed pictrue elements to " + json_path1)


def time_list_line(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,show = False,dpi = 300,title = None,
                   sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    ids.sort()
    nids = len(ids)
    if isinstance(title, list):
        if nids != len(title):
            if meteva.base.language =="ch":
                print("手动设置的title数目和要绘制的图形数目不一致")
            else:
                print("title count is different from fig count")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids != len(save_path):
            if meteva.base.language =="ch":
                print("手动设置的save_path数目和要绘制的图形数目不一致")
            else:
                print("save_path count is different from fig count")
            return

    if title is None:
        if meteva.base.language=="ch":
            title = "预报准确性和稳定性对比图"
        else:
            title = "Forecast Accuracy and Stability"
    for n in range(nids):
        id = ids[n]
        #print(id)
        sta_ob_and_fos = meteva.base.in_id_list(sta_ob_and_fos1,[id])
        times_fo = sta_ob_and_fos.loc[:, "time"].values
        times_fo = list(set(times_fo))
        if (len(times_fo) == 1):
            if meteva.base.language == "ch":
                print("仅有单个起报时间的预报，程序退出")
            else:
                print("only forecast of one start time，progress end")
            return
        times_fo.sort()
        times_fo = np.array(times_fo)
        dhs_fo = (times_fo[1:] - times_fo[0:-1])
        if isinstance(dhs_fo[0], np.timedelta64):
            dhs_fo = dhs_fo / np.timedelta64(1, 'h')
        else:
            dhs_fo = dhs_fo / datetime.timedelta(hours=1)
        dhs_fo_not0 = dhs_fo[dhs_fo != 0]
        dh_y = np.min(dhs_fo_not0)

        dhs = list(set(sta_ob_and_fos.loc[:, "dtime"].values))
        dhs.sort()
        dhs = np.array(dhs)
        # 以观预报时效间隔的最小单位
        ddhs = dhs[1:] - dhs[0:-1]
        dh_x = int(np.min(ddhs))

        if width is None:
            width = len(dhs) * 1.2
            if width > 8:width = 8
            if width < 4:width = 4

        if height is None:
            height = len(times_fo) * 1
            if height > 5:height = 5

        fig = plt.figure(figsize=(width, height),dpi = dpi)
        grid_plt = plt.GridSpec(len(times_fo), 1, hspace=0)

        time_f0 = times_fo[0]
        data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
        values = sta_ob_and_fos.iloc[:, 6:].values.flatten()
        values = values[values != meteva.base.IV]
        vmax = np.max(values)
        vmin = np.min(values) - 0.1
        vmax = (vmax - vmin) * 1.2 + vmin


        dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
        obtimes = sta_ob_and_fos['time'] + dtimes
        #obtimes[-1] = times_fo[0]
        time_all = list(set(obtimes))
        time_all.sort()
        #print(time_all)
        dtime_all = pd.Series(time_all) - times_fo[0]
        x_all = dtime_all/np.timedelta64(1, 'h')
        x_all = x_all.values
        x_plot,time_strs = meteva.product.program.get_x_ticks(time_all,width-1)
        x_plot += x_all[0]

        time_strs_null = []
        for i in range(len(time_strs)):
            time_strs_null.append("")

        all_y_label = []
        picture_ele_dict = {}
        picture_ele_dict["xticklabels"] = meteva.product.program.fun.get_time_str_list(time_all,row=3)
        picture_ele_dict["vmin"] = vmin
        picture_ele_dict["vmax"] = vmax
        picture_ele_dict["subplots"] ={}

        for i in range(len(times_fo)):
            ax = plt.subplot(grid_plt[i:i + 1, 0])
            picture_ele_dict["subplots"][i] = {}
            time_f1 = times_fo[-i - 1]
            dhour0 = (time_f1 - time_f0) / np.timedelta64(1, 'h')
            sta = meteva.base.in_time_list(sta_ob_and_fos, [time_f1])
            sta = sta.sort_values("dtime")
            x = dhour0 + sta.loc[:, "dtime"].values
            for name in data_names:
                value = sta.loc[:, name].values
                index_iv = np.where(value == meteva.base.IV)
                dat0_all = meteva.base.tool.plot_tools.set_plot_IV_with_out_start_end(value)
                plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                x_iv = x[index_iv[0]]
                dat0_iv = dat0_all[index_iv[0]]
                plt.plot(x_iv, dat0_iv, ".", color='k',markersize = sup_fontsize * 0.1)
                dat0_notiv = value.copy()
                dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                plt.plot(x, dat0_notiv, label=name,marker = ".",linewidth = sup_fontsize * 0.1,markersize = sup_fontsize * 0.3)


                plt.ylim(vmin, vmax)
                plt.yticks(fontsize = sup_fontsize * 0.6)
                plt.xlim(x_all[0],x_all[-1])
                plt.grid(linestyle='-.')

                picture_ele_dict["subplots"][i][name] = {}
                picture_ele_dict["subplots"][i][name]["x"] = x.tolist()
                picture_ele_dict["subplots"][i][name]["value"] = value.tolist()

            time_f1 = meteva.base.tool.time_tools.all_type_time_to_datetime(time_f1)
            if meteva.base.language=="ch":
                time_str = time_f1.strftime('%d{d}%H{h}').format(d='日', h='时')+"        "
            else:
                time_str = time_f1.strftime(' %m-%d %H:%M') + "           "
            all_y_label.append(time_str)
            plt.ylabel(time_str, rotation='horizontal',fontsize = sup_fontsize *0.75)
            if i ==0:
                plt.legend(loc="upper left", ncol=len(data_names),fontsize = sup_fontsize *0.9)
                s1 = s
                if s1 is None:
                    s1 = {}
                s1["id"] = id

                if isinstance(title, list):
                    title1 = title[n]
                else:
                    title1 = meteva.product.program.get_title_from_dict(title, s1, None, None,
                                                                        None)
                    title1 = title1.replace("\n", "")
                plt.title(title1, fontsize=sup_fontsize)
                picture_ele_dict["title"] = title1

            if i == len(times_fo) - 1:
                #print(x_plot)
                plt.xticks(x_plot, time_strs,fontsize = sup_fontsize * 0.8)
                if meteva.base.language=="ch":
                    plt.xlabel("实况时间",fontsize = sup_fontsize * 0.9)
                else:
                    plt.xlabel("Observation time", fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks(x_plot,time_strs_null)

        picture_ele_dict["y_label"] = all_y_label

        if meteva.base.language =="ch":
            rect_ylabel = [0.03, 0.45, 0.0, 0.0]  # 左下宽高
            ax_ylabel = plt.axes(rect_ylabel)
            ax_ylabel.axes.set_axis_off()
            plt.text(0, 0, "起报时间", fontsize=sup_fontsize * 0.9, rotation=90)
        else:
            rect_ylabel = [0.00, 0.45, 0.0, 0.0]  # 左下宽高
            ax_ylabel = plt.axes(rect_ylabel)
            ax_ylabel.axes.set_axis_off()
            plt.text(0, 0, "time", fontsize=sup_fontsize * 0.9, rotation=90)
        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir+"/" + str(id) + ".png"
        else:
            save_path1 = save_path[n]
        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            if meteva.base.language=="ch":
                print("图片已保存至" + save_path1)
            else:
                print("fig has been saved to " + save_path1)
        if show:
            plt.show()
        plt.close()
        json_path1 = None
        if json_path is None:
            if json_dir is None:
                pass
            else:
                json_path1 = json_dir+"/" + str(id) + ".json"
        else:
            json_path1 = json_path[n]

        if json_path1 is not None:
            meteva.base.tool.path_tools.creat_path(json_path1)
            file = open(json_path1,"w")
            json.dump(picture_ele_dict,file)
            print("have printed pictrue elements to " + json_path1)



def time_list_mesh_error(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,
                   max_error = None,cmap_error = None,show = False,xtimetype = "mid",dpi = 300,annot =0,title = "多时效预报误差对比图",
                         sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    '''

    :param sta_ob_and_fos0:
    :param s:
    :param save_dir:
    :param save_path:
    :param clev:
    :param cmap:
    :param plot_error:
    :param cmap_error:
    :param show:
    :param title:
    :return:
    '''

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        dvalues = values[1:,:] - values[0,:]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    sta_ob_and_fos1 = meteva.base.sele_by_para(sta_ob_and_fos1,drop_IV=True)
    if(len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return
    ids = list(set(sta_ob_and_fos1.loc[:, "id"]))
    ids.sort()
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    times_fo = sta_ob_and_fos1.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)
    #print(times_fo)

    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_fo[0], np.timedelta64):
        dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    else:
        dhs_fo = dhs_fo / datetime.timedelta(hours=1)
    dhs_fo_not0 = dhs_fo[dhs_fo != 0]
    dh_y = np.min(dhs_fo_not0)
    min_dtime = int(np.min(sta_ob_and_fos1["dtime"]))


    ob_time_s = sta_ob_and_fos1["time"] + sta_ob_and_fos1["dtime"] * np.timedelta64(1, 'h')
    times_ob = list(set(ob_time_s.values))
    times_ob.sort()
    times_ob = np.array(times_ob)

    dhs_ob = (times_ob[1:] - times_ob[0:-1])
    if isinstance(dhs_ob[0], np.timedelta64):
        dhs_ob = dhs_ob / np.timedelta64(1, 'h')
    else:
        dhs_ob = dhs_ob / datetime.timedelta(hours=1)

    dhs_ob_not0 = dhs_ob[dhs_ob != 0]
    dh_x = np.min(dhs_ob_not0)
    #print(dh_x)
    np.sum(dhs_fo_not0)
    row = int(np.sum(dhs_fo_not0)/dh_y)+1
    col = int(np.sum(dhs_ob_not0)/dh_x)+1
    #print(row)
    t_ob = []
    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))

    y_ticks = []
    t_fo0= meteva.base.all_type_time_to_datetime(times_fo[0])
    step = int(math.ceil(row / 40))

    if step !=1 :
        while step * dh_y % 3 !=0:
            step +=1

    y_plot = np.arange(0,row,step)+0.
    yticklabels = []
    for j in range(0,row,1):
        jr = row - j - 1
        time_fo = t_fo0 + datetime.timedelta(hours=1) * dh_y * jr
        hour = time_fo.hour
        day = time_fo.day
        str1 = str(day) + "日" + str(hour) + "时"
        yticklabels.append(str1)
        if j%step ==0:
            y_ticks.append(str1)

    if width is None:
        width = 8

    x_plot,x_ticks = meteva.product.get_x_ticks(times_ob,width-2)
    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+0.5
    elif xtimetype == "left":
        x_plot = x_plot -0.5
    else:
        x_plot = x_plot

    if col >=120:
        annot = None
    # if annot:
    #     annot = col <120

    annot_size = width * 50 / col
    if annot_size >16:
        annot_size= 16

    nids = len(ids)
    nfo = len(data_names) - 1
    if isinstance(title, list):
        if nids * nfo != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk = 0
    for d in range(nfo):
        data_name = data_names[d+1]
        sta_one_member = meteva.base.in_member_list(sta_ob_and_fos1, [data_names[0],data_name])
        #meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        #sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        #以最近的预报作为窗口中间的时刻
        for id in ids:
            picture_ele_dict = {}
            picture_ele_dict["xticklabels"] = meteva.product.program.fun.get_time_str_list(times_ob, row=3)
            picture_ele_dict["yticklabels"] = yticklabels
            
            sta_one_id = meteva.base.in_id_list(sta_one_member,id)
            dat = np.ones((col, row)) * meteva.base.IV
            for j in range(row):
                jr = row - j - 1
                time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                sta_on_row = meteva.base.in_time_list(sta_one_id,time_fo)
                dhx0 = (time_fo - times_ob[0])/np.timedelta64(1, 'h')
                dhxs = sta_on_row["dtime"].values + dhx0
                index_i = (dhxs/dh_x).astype(np.int16)
                dat[index_i,j] = sta_on_row.values[:,-1] - sta_on_row.values[:,-2]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True
            picture_ele_dict["error"] = dat.tolist()

            if height is None:
                height = width * row / col + 2
            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


            if cmap_error is None:
                cmap_error =meteva.base.cmaps.me_bwr

            #sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=annot,fmt='.0f'
            #, annot_kws = {'size': annot_size})

            cmap_part,clevs = meteva.base.color_tools.def_cmap_clevs(cmap_error,vmin = -maxd,vmax = maxd)
            meteva.base.tool.myheatmap(ax2, dat.T, cmap = cmap_part,clevs=clevs,  annot=annot, fontsize=sup_fontsize * 0.8)

            ax2.set_xlabel('实况时间',fontsize = sup_fontsize *  0.9)
            ax2.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)
            
            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row-0.5, -0.5)
            s1 = s
            if s1 is None:
                s1 = {}
                s1["id"] = id
                s1["member"] =[data_name]
            if isinstance(title,list):
                title1 = title[kk]
            else:
                if id in meteva.base.station_id_name_dict.keys():
                    title1 = title + "(" + data_name + ")" + "{\'id\':" + str(id) +meteva.base.station_id_name_dict[id] +"}"
                else:
                    title1 = title + "(" + data_name + ")" + "{\'id\':" + str(id) +  "}"

            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
            rect = patches.Rectangle((-0.5,-0.5), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if(save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir +"/" +data_name+"_"+str(id) + ".png"
            else:
                save_path1 = save_path[kk]
            if save_path1 is not None:

                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1,bbox_inches='tight')
                print("图片已保存至"+save_path1)
            if show:
                plt.show()
            plt.close()

            json_path1 = None
            if json_path is None:
                if json_dir is None:
                    pass
                else:
                    json_path1 = json_dir + "/" + data_name + "_" + str(id) + ".json"
            else:
                json_path1 = json_path[kk]

            if json_path1 is not None:
                meteva.base.tool.path_tools.creat_path(json_path1)
                file = open(json_path1, "w")
                json.dump(picture_ele_dict, file)
                print("have printed pictrue elements to " + json_path1)
            kk += 1
    return

def time_list_mesh(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,
                   clevs = None,cmap = None,plot_error = True,max_error = None,cmap_error= None,
                   show = False,xtimetype = "mid",dpi = 300,annot =0,title = "预报准确性和稳定性对比图",
                   sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    '''

    :param sta_ob_and_fos0:
    :param s:
    :param save_dir:
    :param save_path:
    :param clev:
    :param cmap:
    :param plot_error:
    :param cmap_error:
    :param show:
    :param title:
    :return:
    '''

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        if(values.size ==0):
            print("无有效的观测数据")
            return
        dvalues = values[1:,:] - values[0,:]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error


    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    ids.sort()
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    sta_ob_all1 = meteva.base.sele_by_para(sta_ob_and_fos1,member=[data_names[0]])
    sta_fo_all1 = meteva.base.sele_by_para(sta_ob_and_fos1, member=data_names[1:])
    times_fo = sta_fo_all1.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)
    #print(times_fo)

    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_fo[0], np.timedelta64):
        dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    else:
        dhs_fo = dhs_fo / datetime.timedelta(hours=1)
    dhs_fo_not0 = dhs_fo[dhs_fo != 0]
    dh_y = np.min(dhs_fo_not0)
    min_dtime = int(np.min(sta_fo_all1["dtime"]))
    sta_ob_part2_list = []
    for ky in range(int(dh_y),int(np.max(sta_ob_all1["dtime"])),int(dh_y)):
        sta_ob_part1 = meteva.base.between_dtime_range(sta_ob_all1,min_dtime+ky-dh_y,min_dtime+ky-0.1)
        sta_ob_part2 = meteva.base.move_fo_time(sta_ob_part1,ky)
        sta_ob_part2_list.append(sta_ob_part2)

    sta_ob_part2_ = meteva.base.concat(sta_ob_part2_list)
    sta_ob_part2 = sta_ob_part2_.drop_duplicates()

    ob_time_s = sta_fo_all1["time"] + sta_fo_all1["dtime"] * np.timedelta64(1, 'h')
    times_ob = list(set(ob_time_s.values))
    times_ob.sort()
    times_ob = np.array(times_ob)

    dhs_ob = (times_ob[1:] - times_ob[0:-1])
    if isinstance(dhs_ob[0], np.timedelta64):
        dhs_ob = dhs_ob / np.timedelta64(1, 'h')
    else:
        dhs_ob = dhs_ob / datetime.timedelta(hours=1)
    dhs_ob_not0 = dhs_ob[dhs_ob != 0]
    dh_x = np.min(dhs_ob_not0)
    #print(dh_x)
    np.sum(dhs_fo_not0)
    row = int(np.sum(dhs_fo_not0)/dh_y)+2
    col = int(np.sum(dhs_ob_not0)/dh_x)+1
    #print(row)
    t_ob = []

    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))

    #t_fo =[]
    #for t in times_fo:
    #    t_fo.append(meteva.base.all_type_time_to_datetime(t))


    y_ticks = []
    t_fo0= meteva.base.all_type_time_to_datetime(times_fo[0])
    step = int(math.ceil(row / 40))

    if step !=1 :
        while step * dh_y % 3 !=0:
            step +=1

    y_plot = np.arange(0,row,step)
    yticklabels = []
    for j in range(0,row,1):
        jr = row - j - 1
        time_fo = t_fo0 + datetime.timedelta(hours=1) * dh_y * jr
        hour = time_fo.hour
        day = time_fo.day
        str1 = str(day) + "日" + str(hour) + "时"
        yticklabels.append(str1)
        if j%step ==0:
            y_ticks.append(str1)


    if width is None:
        width = 8
    x_plot,x_ticks = meteva.product.get_x_ticks(times_ob,width-2)
    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+0.5
    elif xtimetype == "left":
        x_plot = x_plot -0.5

    if col >=120:
        annot = None
    # if annot:
    #     annot = col <120
    annot_size = width * 50 / col
    if annot_size >16:
        annot_size= 16

    nids = len(ids)
    nfo = len(data_names) - 1
    if isinstance(title, list):
        if plot_error:
            if 2 * nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return
        else:
            if nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk1 = 0
    kk2 = 0
    for d in range(len(data_names)-1):
        data_name = data_names[d+1]
        sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1, data_name)
        meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        #以最近的预报作为窗口中间的时刻

        for id in ids:
            picture_ele_dict = {}
            picture_ele_dict["xticklabels"] = meteva.product.program.fun.get_time_str_list(times_ob, row=3)
            picture_ele_dict["yticklabels"] = yticklabels

            sta_one_id = meteva.base.in_id_list(sta_one_member,id)
            dat = np.ones((col, row)) * meteva.base.IV
            for j in range(row):
                jr = row - j - 1
                time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                sta_on_row = meteva.base.in_time_list(sta_one_id,time_fo)
                #print(sta_on_row)
                dhx0 = (time_fo - times_ob[0])/np.timedelta64(1, 'h')
                dhxs = sta_on_row["dtime"].values + dhx0
                index_i = (dhxs/dh_x).astype(np.int16)
                dat[index_i,j] = sta_on_row.values[:,-1]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True
            picture_ele_dict["dat"] = dat.tolist()
            vmin = np.min(dat[dat != meteva.base.IV])
            vmax = np.max(dat[dat != meteva.base.IV])
            #print(vmax)
            if plot_error:
                if height is None:
                    height = (width * row / col + 2) * 2
                f, (ax1, ax2)  = plt.subplots(figsize=(width, height),nrows = 2,edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90,hspace=0.3)
                dvalue = np.zeros_like(dat)
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat[i, j] != meteva.base.IV:
                            top_value = dat[i, j]
                            break
                    for j in range(row):
                        if dat[i, j] != meteva.base.IV:
                            dvalue[i, j] = dat[i, j] - top_value

                dvalue[dat == meteva.base.IV] = meteva.base.IV
                picture_ele_dict["error"] = dvalue.tolist()

                if cmap_error is None:
                    cmap_error = "me_bwr"
                cmap_part_e, clevs_e = meteva.base.color_tools.def_cmap_clevs(cmap_error, vmin=-maxd, vmax=maxd)

                meteva.base.tool.myheatmap(ax1, dvalue.T, cmap=cmap_part_e, clevs=clevs_e, annot=annot,fontsize=annot_size)
                #sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=annot,
                #             fmt=fmt_str, annot_kws={'size':annot_size})

                #ax1.set_xlabel('实况时间',fontsize = sup_fontsize = 0.9)
                ax1.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
                ax1.set_xticks(x_plot)
                ax1.set_xticklabels(x_ticks,rotation=360,fontsize=sup_fontsize * 0.8)
                ax1.set_yticks(y_plot)
                ax1.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)

                if isinstance(title,list):
                    title1 = title[kk2]
                    kk2 +=1
                else:
                    if id in meteva.base.station_id_name_dict.keys():
                        title1 = title+"（误差）"+"("+data_name+")"+ "{\'id\':"+str(id)+meteva.base.station_id_name_dict[id] +"}"
                    else:
                        title1 = title + "（误差）" + "(" + data_name + ")" + "{\'id\':" + str(id) + "}"
                ax1.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)

                ax1.grid(linestyle='--', linewidth=0.5)

                #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
                plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
                plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内
                picture_ele_dict["ob_rect"] = []

                for k in range(row + 1):
                    jr = row - k - 1
                    time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                    dhx0 = (time_fo- times_ob[0]) / np.timedelta64(1, 'h') + min_dtime
                    x1 = (dhx0 - dh_y) / dh_x
                    y1 = k
                    rect = patches.Rectangle((x1-0.5, y1-0.5), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    picture_ele_dict["ob_rect"].append([x1,y1,dh_y/dh_x,1])
                    ax1.add_patch(rect)
                rect = patches.Rectangle((-0.5, -0.5), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
                ax1.set_ylim(row-0.5, -0.5)
                ax1.add_patch(rect)
            else:
                if height is None:
                    height = width * row / col + 1.2
                f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            if cmap is None:
                cmap = "rainbow"
            cmap_part ,clev_part= meteva.base.tool.color_tools.def_cmap_clevs(cmap,clevs,vmin,vmax)
            # sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt='.0f'
            # , annot_kws = {'size': annot_size})

            meteva.base.tool.myheatmap(ax2, dat.T, cmap = cmap_part,clevs=clev_part,  annot=annot, fontsize=annot_size)
            ax2.set_xlabel('实况时间',fontsize = sup_fontsize * 0.9)
            ax2.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.grid(linestyle='--', linewidth=0.5)

            ax2.set_ylim(row-0.5,-0.5)
            s1 = s
            if s1 is None:
                s1 = {}
                s1["id"] = id
                s1["member"] =[data_name]
            #title1 = meteva.product.program.get_title_from_dict(meteva.product.time_list_mesh, s1, None, None,None)

            #title = data_name + '实况和不同时效预报对比图'
            if isinstance(title,list):
                title1 = title[kk2]
                kk2 +=1
            else:
                if id in meteva.base.station_id_name_dict.keys():
                    title1 = title + "（要素值）" + "(" + data_name + ")" + "{\'id\':" + str(id) +meteva.base.station_id_name_dict[id] +"}"
                else:
                    title1 = title + "（要素值）" + "(" + data_name + ")" + "{\'id\':" + str(id)  + "}"
            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)

            for k in range(row):
                jr = row - k - 1
                dhx0 = (times_fo[0] - times_ob[0]) / np.timedelta64(1, 'h') +min_dtime + dh_y * jr
                x1 = (dhx0-dh_y)/dh_x
                y1 = k
                rect = patches.Rectangle((x1-0.5, y1-0.5), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)
            rect = patches.Rectangle((-0.5,-0.5 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if (save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir + "/" + data_name + "_" + str(id) + ".png"
            else:
                save_path1 = save_path[kk1]
            if save_path1 is not None:
                meteva.base.tool.path_tools.creat_path(save_path1)
                figure = plt.gcf()
                plt.tight_layout()
                figure.savefig(save_path1, bbox_inches='tight')
                print("图片已保存至" + save_path1)
            if show:
                plt.show()
            plt.close()
            json_path1 = None
            if json_path is None:
                if json_dir is None:
                    pass
                else:
                    json_path1 = json_dir + "/" + data_name + "_" + str(id) + ".json"
            else:
                json_path1 = json_path[kk1]

            if json_path1 is not None:
                meteva.base.tool.path_tools.creat_path(json_path1)
                file = open(json_path1, "w")
                json.dump(picture_ele_dict, file)
                print("have printed pictrue elements to " + json_path1)
            kk1 += 1
    return



def time_list_mesh_temp(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                        title = "温度预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,cmap_error= "bwr",show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)

def time_list_mesh_rain01h(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                           title = "1小时降水量预报准确性和稳定性对比图",
                           sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rain_1h")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,show = show,xtimetype="right",dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)

def time_list_mesh_rain03h(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                           title = "3小时降水量预报准确性和稳定性对比图",
                           sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rain_3h")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h_error")
    time_list_mesh(sta_ob_and_fos0, s, save_dir, save_path, clev, cmap, plot_error, show=show,
                    xtimetype="right",dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)

def time_list_mesh_rh(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                      title = "相对湿度预报准确性和稳定性对比图",
                      sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rh")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rh_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path, clev, cmap, plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)

def time_list_mesh_vis(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                       title = "能见度预报准确性和稳定性对比图",
                       sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("vis")
    #clev_error,cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("vis_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)


def time_list_mesh_tcdc(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =0,
                        title = "云量预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("tcdc")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("tcdc_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error = plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height,json_dir = json_dir,json_path = json_path)


def time_list_mesh_wind(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,
                        max_error = None,show = False,dpi = 300,title = "风预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None,json_dir = None,json_path = None):

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        if(values.size ==0):
            print("无有效的观测数据")
            return
        u = values[0::2,:]
        v = values[1::2,:]
        s2 = u * u +v * v
        speed = np.sqrt(s2.astype(np.float32))
        dvalues = speed[1:, :] - speed[0, :]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error


    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:, "id"]))
    ids.sort()
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    ob_names = data_names[0:2]
    fo_names = data_names[2:]
    sta_ob_all1 = meteva.base.sele_by_para(sta_ob_and_fos1,member=ob_names)
    sta_fo_all1 = meteva.base.sele_by_para(sta_ob_and_fos1, member=fo_names)

    times_fo = sta_fo_all1.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)
    # print(times_fo)

    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_fo[0], np.timedelta64):
        dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    else:
        dhs_fo = dhs_fo / datetime.timedelta(hours=1)
    dhs_fo_not0 = dhs_fo[dhs_fo != 0]
    dh_y = np.min(dhs_fo_not0)
    min_dtime = int(np.min(sta_fo_all1["dtime"]))
    sta_ob_part1 = meteva.base.between_dtime_range(sta_ob_all1, min_dtime, min_dtime + dh_y - 0.1)
    sta_ob_part2 = meteva.base.move_fo_time(sta_ob_part1, dh_y)

    ob_time_s = sta_fo_all1["time"] + sta_fo_all1["dtime"] * np.timedelta64(1, 'h')
    times_ob = list(set(ob_time_s.values))
    times_ob.sort()
    times_ob = np.array(times_ob)

    dhs_ob = (times_ob[1:] - times_ob[0:-1])
    if isinstance(dhs_ob[0], np.timedelta64):
        dhs_ob = dhs_ob / np.timedelta64(1, 'h')
    else:
        dhs_ob = dhs_ob / datetime.timedelta(hours=1)
    dhs_ob_not0 = dhs_ob[dhs_ob != 0]
    dh_x = np.min(dhs_ob_not0)
    # print(dh_x)
    np.sum(dhs_fo_not0)
    row = int(np.sum(dhs_fo_not0) / dh_y) + 2
    col = int(np.sum(dhs_ob_not0) / dh_x) + 1
    # print(row)
    t_ob = []
    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))

    # t_fo =[]
    # for t in times_fo:
    #    t_fo.append(meteva.base.all_type_time_to_datetime(t))

    y_plot = np.arange(row) + 0.5
    y_ticks = []
    t_fo0 = meteva.base.all_type_time_to_datetime(times_fo[0])
    step = int(math.ceil(row / 40))

    if step != 1:
        while step * dh_y % 3 != 0:
            step += 1

    y_plot = np.arange(0, row, step)
    for j in range(0, row, step):
        jr = row - j - 1
        time_fo = t_fo0 + datetime.timedelta(hours=1) * dh_y * jr
        hour = time_fo.hour
        day = time_fo.day
        # if ((j * int(dh_y)) % 3 == 0):
        str1 = str(day) + "日" + str(hour) + "时"
        # else:
        #    str1 = str(hour) + "时"
        # print(str1)
        y_ticks.append(str1)

    if width is None:
        width = 8
    x_plot, x_ticks = meteva.product.get_x_ticks(times_ob, width - 2)
    x_plot /= dh_x
    x = np.arange(col)
    y = np.arange(row)
    nfo = int(len(fo_names)/2)
    nids = len(ids)
    if isinstance(title, list):
        if plot_error:
            if 2 * nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return
        else:
            if nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk1 = 0
    kk2 = 0

    lenght = 40 * (width / col)
    lenght =1.7* lenght**0.5
    for d in range(nfo):
        data_name = fo_names[d*2:d*2+2]
        sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1, data_name)
        meteva.base.set_stadata_names(sta_ob_part2, data_name)
        sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        # 以最近的预报作为窗口中间的时刻
        for id in ids:
            picture_ele_dict = {}
            picture_ele_dict["xticklabels"] = meteva.product.program.fun.get_time_str_list(times_ob, row=3)
            picture_ele_dict["subplots"] = {}

            sta_one_id = meteva.base.in_id_list(sta_one_member, id)
            #dat = np.ones((col, row)) * meteva.base.IV
            dat_u = np.ones((row,col)) * meteva.base.IV
            dat_v = np.ones(dat_u.shape)* meteva.base.IV
            for j in range(row):
                jr = row - j - 1
                time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                #print(time_fo)
                sta_on_row = meteva.base.in_time_list(sta_one_id, time_fo)
                dhx0 = (time_fo - times_ob[0]) / np.timedelta64(1, 'h')
                dhxs = sta_on_row["dtime"].values + dhx0
                index_i = (dhxs / dh_x).astype(np.int16)

                dat_u[j,index_i] = sta_on_row.values[:, -2]
                dat_v[j,index_i] = sta_on_row.values[:, -1]
            dat_speed = np.sqrt(dat_u * dat_u + dat_v*dat_v)
            dat_speed[dat_u == meteva.base.IV] = meteva.base.IV
            mask = np.zeros_like(dat_speed)
            mask[dat_speed == meteva.base.IV] = True

            if plot_error:
                if height is None:
                    height = (width * row / col + 2) * 2
                f, (ax1, ax2) = plt.subplots(figsize=(width, height), nrows=2, edgecolor='black', dpi=dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90, hspace=0.3)

                #lenght = 5*(height / row)
                #print(lenght)
                diff_speed = np.zeros_like(dat_speed)
                diff_u = np.zeros_like(dat_u)
                diff_v = np.zeros_like(dat_v)

                # "风速误差"
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_speed[j, i] != meteva.base.IV:
                            top_value = dat_speed[j, i]
                            break
                    for j in range(row):
                        if dat_speed[j, i] != meteva.base.IV:
                            diff_speed[j, i] = dat_speed[j, i] - top_value
                # u 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_u[j, i] != meteva.base.IV:
                            top_value = dat_u[j, i]
                            break
                    for j in range(row):
                        if dat_u[j, i] != meteva.base.IV:
                            diff_u[j, i] = dat_u[j, i] - top_value
                # v 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_v[j, i] != meteva.base.IV:
                            top_value = dat_v[j, i]
                            break
                    for j in range(row):
                        if dat_v[j, i] != meteva.base.IV:
                            diff_v[j, i] = dat_v[j, i] - top_value


                cmap_part_e, clevs_e = meteva.base.color_tools.def_cmap_clevs("me_bwr", vmin=-maxd, vmax=maxd)

                meteva.base.tool.myheatmap(ax1, diff_speed, cmap=cmap_part_e, clevs=clevs_e, annot=None)

                #clev, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed_error")

                #sns.heatmap(diff_speed, ax=ax1, mask=mask, cmap="bwr", vmin=-maxd, vmax=maxd)
                # sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                #            fmt=fmt_str)
                #ax1.set_xlabel('实况时间',fontsize =16 )
                ax1.set_ylabel('起报时间',fontsize =sup_fontsize * 0.9)
                ax1.set_xticks(x_plot)
                ax1.set_xticklabels(x_ticks,fontsize =sup_fontsize * 0.8)
                ax1.set_yticks(y_plot)
                ax1.set_yticklabels(y_ticks, rotation=360,fontsize =sup_fontsize * 0.8)
                #title = "实况(id:" + str(id) + ")和不同时效预报(" + data_name[0][2:] + ")偏差图"
                if isinstance(title,list):
                    title1 = title[kk2]
                    kk2 += 1
                else:

                    if id in meteva.base.station_id_name_dict.keys():
                        title1 = title + "(偏差)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id) + meteva.base.station_id_name_dict[id] + "}"
                    else:
                        title1 = title + "(偏差)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id) + "}"

                ax1.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
                ax1.grid(linestyle='--', linewidth=0.5)
                xx, yy = np.meshgrid(x , y )
                speed_1d = dat_speed.flatten()
                xx_1d = xx.flatten()[speed_1d != meteva.base.IV]
                yy_1d = yy.flatten()[speed_1d != meteva.base.IV]
                u_1d = diff_u.flatten()[speed_1d != meteva.base.IV]
                v_1d = diff_v.flatten()[speed_1d != meteva.base.IV]
                ax1.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20},
                          length=lenght,sizes = dict(emptybarb=0.01, spacing=0.23, height=0.5, width=0.25),
                      linewidth = lenght * lenght * 0.025)

                plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
                plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内
                for k in range(row-1):
                    jr = row - k - 1
                    #dhx0 = (times_fo[jr] - times_ob[0]) / np.timedelta64(1, 'h') + min_dtime
                    #time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                    #dhx0 = (times_fo[jr] - times_ob[0]) / np.timedelta64(1, 'h') + min_dtime
                    dhx0 = (times_fo[0] - times_ob[0]) / np.timedelta64(1, 'h') + min_dtime + dh_y * jr
                    x1 = (dhx0 - dh_y) / dh_x
                    y1 = k
                    rect = patches.Rectangle((x1-0.5, y1-0.5), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    ax1.add_patch(rect)
                rect = patches.Rectangle((-0.5, -0.5), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
                #ax1.add_patch(rect)
                ax1.set_ylim(row - 0.5, -0.5)
            else:
                if height is None:
                    height = width * row / col + 1.2
                f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black', dpi=dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

                #lenght = (height / row)
                #print(lenght)
            vmin = np.min(dat_speed[dat_speed != meteva.base.IV])
            vmax = np.max(dat_speed[dat_speed != meteva.base.IV])
            cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("wind_speed")
            cmap_part,clev_part  = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap,clev, vmax, vmin)
            vmax = clev_part[-1]
            vmin = 2 * clev_part[0] - clev_part[1]

            #sns.heatmap(dat_speed, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax)

            cmap_part ,clev_part= meteva.base.tool.color_tools.def_cmap_clevs("wind_speed")
            # sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt='.0f'
            # , annot_kws = {'size': annot_size})


            meteva.base.tool.myheatmap(ax2, dat_speed, cmap = cmap_part,clevs=clev_part,  annot=None)

            ax2.set_xlabel('实况时间',fontsize =sup_fontsize * 0.9)
            ax2.set_ylabel('起报时间',fontsize =sup_fontsize * 0.8)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,fontsize =sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360,fontsize =sup_fontsize * 0.8)
            #title = "实况(" + str(id) + ")和不同时效预报(" + data_name[0][2:] + ")对比图"
            if isinstance(title,list):
                title1 = title[kk2]
                kk2+= 1
            else:
                if id in meteva.base.station_id_name_dict.keys():
                    title1 = title + "(要素值)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id) + \
                             meteva.base.station_id_name_dict[id] + "}"
                else:
                    title1 = title + "(要素值)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id)  +"}"

            ax2.set_ylim(row - 0.5, -0.5)
            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
            ax2.grid(linestyle='--', linewidth=0.5)
            xx, yy = np.meshgrid(x , y )
            speed_1d = dat_speed.flatten()
            xx_1d = xx.flatten()[speed_1d != meteva.base.IV]
            yy_1d = yy.flatten()[speed_1d != meteva.base.IV]
            u_1d = dat_u.flatten()[speed_1d != meteva.base.IV]
            v_1d = dat_v.flatten()[speed_1d != meteva.base.IV]

            ax2.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20},
                      length=lenght,sizes = dict(emptybarb=0.01, spacing=0.23, height=0.5, width=0.25),
                      linewidth = lenght * lenght * 0.025)

            for k in range(row-1):
                jr = row - k - 1
                dhx0 = (times_fo[0] - times_ob[0]) / np.timedelta64(1, 'h') +min_dtime + dh_y * jr
                x1 = (dhx0-dh_y)/dh_x
                y1 = k
                rect = patches.Rectangle((x1-0.5, y1-0.5), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)
            #rect = patches.Rectangle((-0.5,-0.5), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            #ax2.add_patch(rect)

            save_path1 = None
            if (save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir + "/" + data_name[0][2:] + "_" + str(id) + ".png"
            else:
                save_path1 = save_path[kk1]
            if save_path1 is not None:
                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1, bbox_inches='tight')
                print("图片已保存至" + save_path1)
            if show:
                plt.show()
            plt.close()
            json_path1 = None
            if json_path is None:
                if json_dir is None:
                    pass
                else:
                    json_path1 = json_dir + "/" + str(id) + ".png"
            else:
                json_path1 = json_path[kk1]

            if json_path1 is not None:
                meteva.base.tool.path_tools.creat_path(json_path1)
                file = open(json_path1, "w")
                json.dump(picture_ele_dict, file)
                print("have printed pictrue elements to " + json_path1)
            kk1 += 1
    return


