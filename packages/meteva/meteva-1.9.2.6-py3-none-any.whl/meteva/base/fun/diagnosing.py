import math
import meteva
import numpy as np
import copy
import pandas as pd
import datetime


def temp_decrease_in_process(sta,used_coords = "dtime"):
    if used_coords == "dtime":
        change_24 = change(sta,delta=24,used_coords="dtime")
        change_48 = change(sta,delta=48,used_coords="dtime")
        change_24_48 = meteva.base.min_on_level_time_dtime_id(change_24,change_48,how="outer",default=0)
        change_most_dtime =  meteva.base.loc_of_min(change_24_48,used_coords=["dtime"],ignore_missing=True)
        change_most_dtime.loc[:,"dtime"] = change_most_dtime.iloc[:,6]
        change_most = meteva.base.min_of_sta(change_24_48,used_coords=["dtime"],ignore_missing=True)
        change_most.attrs = copy.deepcopy(sta.attrs)
        return change_most

def accumulate_time(sta_ob,step,keep_all = True):
    '''
    观测数据累加
    :param sta_ob:
    :param step:
    :param keep_all:
    :return:
    '''

    times= sta_ob.loc[:,'time'].values
    times = list(set(times))
    times.sort()
    times = np.array(times)
    dtimes = times[1:] - times[0:-1]
    min_dtime = np.min(dtimes)
    rain_ac = None
    for i in range(step):
        rain1 = sta_ob.copy()
        rain1["time"] = rain1["time"] + min_dtime * i
        rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac,rain1,how="inner")
    if not keep_all:
        dtimes = times[:] - times[-1]
        dh = (dtimes/min_dtime).astype(np.int32)
        new_times = times[dh%step ==0]
        rain_ac = meteva.base.in_time_list(rain_ac,new_times)
    print("warning: accumulate_time函数将在后续升级中不再支持，请重新使用sum_of_sta函数满足相关需求")
    return rain_ac

def accumulate_dtime(sta,step,keep_all = True):
    '''观测数据累加'''

    dtimes= sta.loc[:,'dtime'].values
    dtimes = list(set(dtimes))
    dtimes.sort()
    dtimes = np.array(dtimes)
    dhour_unit = dtimes[0]
    if dhour_unit ==0:
        dhour_unit = dtimes[1]
    rain_ac = None
    for i in range(step):
        rain1 = sta.copy()
        rain1["dtime"] = rain1["dtime"] + dhour_unit * i
        #print(dhour_unit * i)
        rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac,rain1,how="inner")
    if not keep_all:
        dh =((dtimes - dtimes[-1])/dhour_unit).astype(np.int32)
        new_dtimes = dtimes[dh%step ==0]
        rain_ac = meteva.base.in_dtime_list(rain_ac,new_dtimes)
    return rain_ac

def change(data,delta = 24,used_coords = "time"):

    if used_coords == "time":
        if isinstance(data,pd.DataFrame):
            names_0 = meteva.base.get_stadata_names(data)
            names_1 = []
            for name in names_0:
                names_1.append(name + "_new")
            sta1 = data.copy()
            meteva.base.set_stadata_names(sta1, names_1)
            sta1["time"] = sta1["time"] + datetime.timedelta(hours= delta)
            sta01 = meteva.base.combine_on_all_coords(sta1, data)
            fn = len(names_1)
            dvalue = sta01.iloc[:, (-fn):].values - sta01.iloc[:, (-fn * 2):(-fn)].values
            sta01.iloc[:, (-fn):] = dvalue
            sta01 = sta01.drop(names_1, axis=1)
            sta01.attrs = copy.deepcopy(data.attrs)
            sta01.attrs["valid_time"] = delta
            return sta01
        else:
            grid0 = meteva.base.get_grid_of_data(data)
            times_all = data["time"].values
            index_dtime = {}
            time1_all = []
            for i in range(len(times_all)):
                time1 = meteva.base.all_type_time_to_datetime(times_all[i])
                time1_all.append(time1)
                index_dtime[time1] = i
            index_s = []
            index_e = []
            for i in range(len(times_all)):
                time_e = time1_all[i]
                time_s = time_e - datetime.timedelta(hours=delta)
                if time_s in index_dtime.keys():
                    index_e.append(i)
                    index_s.append(index_dtime[time_s])
            time_list_e = times_all[index_e]
            if len(time_list_e) ==0:
                gtime1 = time_list_e
            else:
                gtime1 = [time_list_e[0],time_list_e[-1],time_list_e[1] - time_list_e[0]]
            dat_delta = data.values[:,:,index_e,:,:,:] - data.values[:,:,index_s,:,:,:]
            grid1 = meteva.base.grid(grid0.glon,grid0.glat,gtime1,grid0.dtimes,grid0.levels,grid0.members)
            grd_change = meteva.base.grid_data(grid1,dat_delta)
            return grd_change
    else:
        if isinstance(data, pd.DataFrame):
            names_0 = meteva.base.get_stadata_names(data)
            names_1 = []
            for name in names_0:
                names_1.append(str(name)+"_new")
            sta1 = data.copy()
            meteva.base.set_stadata_names(sta1,names_1)
            sta1.loc[:,"dtime"] = sta1.loc[:,"dtime"] + delta
            sta01 = meteva.base.combine_on_all_coords(sta1,data)
            fn= len(names_1)
            dvalue = sta01.iloc[:,(-fn):].values - sta01.iloc[:,(-fn * 2):(-fn)].values
            sta01.iloc[:,(-fn):] = dvalue
            sta01 = sta01.drop(names_1,axis=1)
            sta01.attrs = copy.deepcopy(data.attrs)
            sta01.attrs["valid_time"] = delta
            return sta01
        else:
            grid0 = meteva.base.get_grid_of_data(data)
            dtimes_all = data["dtime"].values
            index_dtime = {}
            for i in range(len(dtimes_all)):
                index_dtime[dtimes_all[i]] = i
            index_s = []
            index_e = []
            for i in range(len(dtimes_all)):
                dtime_e = dtimes_all[i]
                dtime_s = dtime_e - delta
                if dtime_s in index_dtime.keys():
                    index_e.append(i)
                    index_s.append(index_dtime[dtime_s])
            dtime_list_e = dtimes_all[index_e]
            dat_delta = data.values[:,:,:,index_e,:,:] - data.values[:,:,:,index_s,:,:]
            grid1 = meteva.base.grid(grid0.glon,grid0.glat,grid0.gtime,dtime_list_e,grid0.levels,grid0.members)
            grd_change = meteva.base.grid_data(grid1,dat_delta)
            return grd_change

def t_rh_to_tw(temp,rh,rh_unit = "%"):
    '''根据温度和相对湿度计算湿球温度'''
    if isinstance(temp,pd.DataFrame):
        sta1 = meteva.base.combine_on_all_coords(temp, rh)
        meteva.base.set_stadata_names(sta1, ["t", "rh"])
        sta2 = meteva.base.not_IV(sta1)
        T = sta2.loc[:,"t"].values
        RH = sta2["rh"].values
        if(T[0]>120):
            T -= 273.16

        if rh_unit == "%":
            pass
        else:
            RH = RH * 100
        max_rh = np.max(RH)
        min_rh = np.min(RH)
        if max_rh>100 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return
        if max_rh < 1:
            print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        Tw = T * np.arctan(0.151977 * np.sqrt(RH + 8.313659)) + np.arctan(T + RH) - np.arctan(
            RH - 1.676331) + 0.00391838 * np.power(RH, 1.5) * np.arctan(0.023101 * RH) - 4.686035

        sta2["tw"] = Tw
        sta = sta2.drop(["t", "rh"], axis=1)
        sta.attrs = copy.deepcopy(sta.attrs)
        sta.attrs["var_name"] = "tw"
        sta.attrs["var_cn_name"] = "湿球温度"
        sta.attrs["var_units"] = "degC"
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)
        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values

        RH = rh.values
        if rh_unit == "%":
            RH /= 100
        else:
            pass
        max_rh = np.max(RH)
        min_rh = np.min(RH)
        if max_rh>1 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return
        if max_rh < 0.01:
            print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        Tw = T * np.arctan(0.151977 * np.sqrt(RH + 8.313659)) + np.arctan(T + RH) - np.arctan(
            RH - 1.676331) + 0.00391838 * np.power(RH, 1.5) * np.arctan(0.023101 * RH) - 4.686035

        grd = meteva.base.grid_data(grid0,Tw)
        return grd

def u_v_to_speed_angle(u,v):
    '''
    将u，v 转换成风速，风向
    :param u:
    :param v:
    :return:
    '''
    if isinstance(u, pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(u, v)
        datanames = meteva.base.get_stadata_names(sta)
        nu = int(len(datanames)/2)
        #nsta = len(sta.indexs)
        ud = sta.iloc[:,6:(6+nu)].values.astype(np.float32)
        vd = sta.iloc[:,(6+nu):].values.astype(np.float32)

        s,a = meteva.base.tool.math_tools.u_v_to_s_d(ud,vd)
        speed = sta.iloc[:,0:(6+nu)].copy()
        angle = speed.copy()
        speed.iloc[:,6:(6+nu)] = s[...]
        angle.iloc[:, 6:(6 + nu)] = a[...]
        names1 = []
        names2 = []
        for i in range(nu):
            names1.append("speed"+str(i))
            names2.append("angle"+str(i))
        meteva.base.set_stadata_names(speed,names1)
        meteva.base.set_stadata_names(angle,names2)
        speed.attrs = copy.deepcopy(u.attrs)
        speed.attrs["var_name"] = "wsp"
        sta.attrs["var_cn_name"] = "风速"
        sta.attrs["var_units"] = "m/s"
        angle.attrs = copy.deepcopy(u.attrs)
        angle.attrs["var_name"] = "wdir"
        angle.attrs["var_cn_name"] = "风向"
        angle.attrs["var_units"] = "degree"
        return speed,angle
    else:
        ud = u.values
        vd = v.values
        s, a = meteva.base.tool.math_tools.u_v_to_s_d(ud, vd)
        grid = meteva.base.get_grid_of_data(u)
        speed = meteva.base.grid_data(grid,s)
        angle = meteva.base.grid_data(grid,a)
        return speed,angle

def u_v_to_wind(u,v):
    if isinstance(u,pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(u, v)
        meteva.base.set_stadata_names(sta, ["u", "v"])
        return  sta

    else:
        grid0 = meteva.base.get_grid_of_data(u)
        grid1 = meteva.base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                                  dtime_list= grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
        wind = meteva.base.grid_data(grid1)
        wind.name = "wind"
        wind.values[0, :, :, :, :, :] = u.values[0, :, :, :, :, :]
        wind.values[1, :, :, :, :, :] = v.values[0, :, :, :, :, :]
        return wind

def wind_to_speed_angle(wind):
    if isinstance(wind,pd.DataFrame):
        member_name = meteva.base.get_stadata_names(wind)
        u = meteva.base.sele_by_para(wind, member=member_name[0::2])
        v =meteva.base.sele_by_para(wind, member=member_name[1::2])
        speed, angle = meteva.base.u_v_to_speed_angle(u, v)
        names = meteva.base.get_stadata_names(u)
        new_names = []
        for name in names:
            if name[0:2] == "u_":
                name = name[2:]
            new_names.append(name)
        meteva.base.set_stadata_names(speed,new_names)
        meteva.base.set_stadata_names(angle,new_names)
        return speed, angle
    else:
        u = meteva.base.in_member_list(wind,member_list=[0],name_or_index="index")
        v = meteva.base.in_member_list(wind, member_list=[1], name_or_index="index")
        speed,angle = u_v_to_speed_angle(u,v)
        return speed,angle

def speed_angle_to_wind(speed,angle = None):
    if isinstance(speed, pd.DataFrame):
        if angle is not None:
            sta = meteva.base.combine_on_all_coords(speed, angle)
        else:
            sta = speed.copy()
        meteva.base.set_stadata_names(sta, ["speed", "angle"])
        #speed = sta["speed"].values.astype(np.float32)
        #angle = sta["angle"].values.astype(np.float32)
        speed = sta["speed"].values.astype(np.float32)
        angle = sta["angle"].values.astype(np.float32)
        u = -speed * np.sin(angle  * math.pi / 180)
        v = -speed * np.cos(angle *  math.pi / 180)
        sta["u"] = u
        sta["v"] = v
        sta = sta.drop(["speed", "angle"], axis=1)
        return sta



    else:
        speed_v = speed.values.squeeze()
        angle_v = angle.values.squeeze()
        grid0 = meteva.base.get_grid_of_data(speed)
        grid1 = meteva.base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                                  dtime_list=grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
        wind = meteva.base.grid_data(grid1)
        wind.name = "wind"
        #wind.values[0, :, :, :, :, :] = speed_v[:, :] * np.cos(angle_v[:, :] * math.pi /180)
        #wind.values[1, :, :, :, :, :] = speed_v[:, :] * np.sin(angle_v[:, :] * math.pi /180)
        wind.values[0, :, :, :, :, :] = -speed_v[:, :] * np.sin(angle_v[:, :] * math.pi /180)
        wind.values[1, :, :, :, :, :] = -speed_v[:, :] * np.cos(angle_v[:, :] * math.pi /180)
        return wind

def t_dtp_to_rh(temp,dtp):
    if isinstance(temp,pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(temp, dtp)
        meteva.base.set_stadata_names(sta, ["t", "dtp"])
        T = sta.loc[:,"t"].values
        if(T[0]>120):
            T -= 273.16

        D = sta["dtp"].values
        if D[0] >120:
            D -= 273.16
        e0 = 6.11 * np.exp(17.15 * T/(235 + T))
        e1 = 6.11 * np.exp(17.15 * D / (235 + D))

        rh = 100 * e1/e0
        sta["rh"] = rh
        sta = sta.drop(["t", "dtp"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)

        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values
        if dtp.values[0,0,0,0,0,0] >120:
            D = dtp.values - 273.16
        else:
            D = dtp.values

        e0 = 6.11 * np.exp(17.15 * T/(235 + T))
        e1 = 6.11 * np.exp(17.15 * D / (235 + D))

        rh = e1/e0
        grd = meteva.base.grid_data(grid0,rh)

        return grd

def t_rh_p_to_q(temp,rh,pressure,rh_unit = "%",check = False):
    '''
    根据温度、相对湿度和气压计算比湿
    :param temp: 温度，可以是摄氏度，也可以是绝对温度
    :param rh:  相对湿度，可以是0-100，也可以是0-1
    :param level: 气压，单位百帕,可以是整数，站点数据或网格数据
    :return:
    '''
    if isinstance(temp,pd.DataFrame):
        if not isinstance(pressure,pd.DataFrame):
            level_s = temp.copy()
            level_s.iloc[:,-1] = pressure
        else:
            level_s = pressure
        sta1 = meteva.base.combine_on_all_coords(temp, rh)
        sta2 = meteva.base.combine_on_all_coords(sta1, level_s)
        meteva.base.set_stadata_names(sta2, ["t", "rh","p"])
        sta2 = meteva.base.not_IV(sta2)
        T = sta2.loc[:,"t"].values
        R = sta2.loc[:,"rh"].values
        P = sta2.loc[:,"p"].values
        if(T[0]>120):
            T -= 273.16
        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622

        if rh_unit == "%":
            R = R.astype(np.float64)
            R = R/100
        else:
            pass

        if check:
            max_rh = np.max(R)
            min_rh = np.min(R)
            if max_rh>1 or min_rh <0:
                print("相对湿度取值不能超过100%或小于0%")
                return
            if max_rh < 0.01:
                print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        q = e0 * R/P
        sta2["q"] = q
        sta = sta2.drop(["t", "rh","p"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)
        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values


        R = rh.values
        if rh_unit == "%":
            R /= 100
        else:
            pass
        if check:
            max_rh = np.max(R)
            min_rh = np.min(R)
            if max_rh>2 or min_rh <0:
                print("相对湿度最大值为"+str(max_rh))
                print("相对湿度最小值为" + str(min_rh))
                print("相对湿度取值不能超过100%或小于0%")
                return None

        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622

        if isinstance(pressure,float) or isinstance(pressure,int):
            P = pressure
        else:
            P = pressure.values
        q = e0 * R/P
        grd = meteva.base.grid_data(grid0,q)
        return grd


def t_rh_to_vp(temp,rh):
    if isinstance(temp,pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(temp, rh)
        meteva.base.set_stadata_names(sta, ["t", "rh"])
        T = sta["t"].values
        R = sta["rh"].values
        if(T[0]>120):
            T -= 273.16
        #e0 = 6.11 * np.exp(17.15 * T/(235 + T))
        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622
        max_rh = np.max(R)
        if max_rh >1.1:
            R /= 100
        vp = e0 * R
        sta["vp"] = vp
        sta = sta.drop(["t", "rh"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)
        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values
        max_rh = np.max(rh.values)
        if max_rh >1.1:
            R = rh.values /100
        else:
            R = rh.values
        #e0 = 6.11 * np.exp(17.15 * T / (235 + T))
        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622
        vp = e0 * R
        grd = meteva.base.grid_data(grid0,vp)
        return grd


def t_q_p_to_rh(temp,q,pressure,unit = "%"):
    '''
    根据温度、比湿和气压计算相对湿度
    :param temp:
    :param q:
    :param pressure:
    :return:
    '''
    rh100 = copy.deepcopy(temp)
    if isinstance(temp, pd.DataFrame):
        rh100.iloc[:,-1] = 100
    else:
        rh100.values[...] = 100
    q100 = t_rh_p_to_q(temp,rh100,pressure)
    if isinstance(temp, pd.DataFrame):
        rh = meteva.base.divide_on_level_time_dtime_id(q,q100)
        if unit == "%":
            rh.iloc[:,6:] *= 100
    else:
        rh = copy.deepcopy(temp)
        rh.values = q.values/q100.values
        #rh.values[rh.values>1] = 1
        if unit=="%":
            rh.values *= 100
    return rh

def t_q_to_rh_on_isobar(temp,q,unit = "%"):
    '''
    根据温度、比湿,以及温度场的气压坐标值计算相对湿度
    :param temp:
    :param q:
    :return:
    '''
    rh100 = copy.deepcopy(temp)
    if isinstance(temp, pd.DataFrame):
        rh100.iloc[:,-1] = 100
    else:
        rh100.values[...] = 100

    if isinstance(temp, pd.DataFrame):
        pressure = copy.deepcopy(temp)
        pressure.iloc[:,-1] = temp["level"].values[:]
        q100 = t_rh_p_to_q(temp, rh100, pressure)
        rh = meteva.base.divide_on_level_time_dtime_id(q,q100)
        if unit == "%":
            rh.iloc[:,6:] *= 100
    else:
        rh = copy.deepcopy(temp)
        pressure = copy.deepcopy(temp)
        levels = pressure["level"].values
        for i in range(levels.size):
            pressure.values[:,i,:,:,:,:] = levels[i]
        q100 = t_rh_p_to_q(temp, rh100, pressure)
        rh.values = q.values/q100.values
        #rh.values[rh.values>1] = 1
        if unit=="%":
            rh.values *= 100
    return rh


def t_to_theta_on_isobar(temp,unit_p = "hPa"):
    '''
    根据温度、比湿,以及温度场的气压坐标值计算相对湿度
    :param temp:
    :param q:
    :return:
    '''


    if isinstance(temp, pd.DataFrame):
        pressure = copy.deepcopy(temp)
        if unit_p.lower()=="hpa":
            pressure.iloc[:, -1] =100 * temp["level"].values[:]
        else:
            pressure.iloc[:, -1] = temp["level"].values[:]

        theta = copy.deepcopy(temp)

        theta.iloc[:,-1] = temp.iloc[:,-1] * np.power(100000/pressure.iloc[:,-1],287/1005)

    else:

        pressure = copy.deepcopy(temp)
        levels = pressure["level"].values
        for i in range(levels.size):
            if unit_p.lower() == "hpa":
                pressure.values[:, i, :, :, :, :] = levels[i]*100
            else:
                pressure.values[:,i,:,:,:,:] = levels[i]
        theta = copy.deepcopy(temp)
        theta.values = temp.values * np.power(100000/pressure.values,287/1005)

    return theta


def gradient(grd):
    lats = grd["lat"].values
    lons = grd["lon"].values
    xx, yy = np.meshgrid(lons, lats)
    dx = np.cos(yy * math.pi / 180)
    gx = np.zeros(grd.values.shape)
    gx[:, :, :, :, :, 1:-1] = (grd.values[:, :, :, :, :, 2:] - grd.values[:, :, :, :, :, :-2]) / 2
    gx[:, :, :, :, :, 0] = grd.values[:, :, :, :, :, 1] - grd.values[:, :, :, :, :, 0]
    gx[:, :, :, :, :, -1] = grd.values[:, :, :, :, :, -1] - grd.values[:, :, :, :, :, -2]
    gx /= (dx * meteva.base.dis_1_degree * 1000)

    gy = np.zeros(grd.values.shape)
    gy[:, :, :, :, 1:-1, :] = (grd.values[:, :, :, :, 2:, :] - grd.values[:, :, :, :, :-2, :]) / 2
    gy[:, :, :, :, 0, :] = grd.values[:, :, :, :, 1, :] - grd.values[:, :, :, :, 0, :]
    gy[:, :, :, :, -1, :] = grd.values[:, :, :, :, -1, :] - grd.values[:, :, :, :, -2, :]
    gy /= (meteva.base.dis_1_degree * 1000)

    grid0 = meteva.base.get_grid_of_data(grd)
    gx_ = meteva.base.grid_data(grid0,gx)
    gy_ = meteva.base.grid_data(grid0,gy)
    grad = meteva.base.u_v_to_wind(gx_,gy_)

    return grad


def uv_to_div(u, v):
    lats = u["lat"].values
    lons = u["lon"].values
    xx, yy = np.meshgrid(lons, lats)
    dx = np.cos(yy * math.pi / 180)
    grid0 = meteva.base.get_grid_of_data(u)
    if(grid0.dlon * grid0.nlon>= 360):
        gx = np.zeros(u.values.shape)
        gx[:, :, :, :, :, 1:-1] = (u.values[:, :, :, :, :, 2:] - u.values[:, :, :, :, :, :-2]) / 2
        gx[:, :, :, :, :, 0] = (u.values[:, :, :, :, :, 1] - u.values[:, :, :, :, :, -1])/2
        gx[:, :, :, :, :, -1] = (u.values[:, :, :, :, :, 0] - u.values[:, :, :, :, :, -2])/2
        gx /= (grid0.dlon * dx * meteva.base.dis_1_degree * 1000)
    else:
        gx = np.zeros(u.values.shape)
        gx[:, :, :, :, :, 1:-1] = (u.values[:, :, :, :, :, 2:] - u.values[:, :, :, :, :, :-2]) / 2
        gx[:, :, :, :, :, 0] = u.values[:, :, :, :, :, 1] - u.values[:, :, :, :, :, 0]
        gx[:, :, :, :, :, -1] = u.values[:, :, :, :, :, -1] - u.values[:, :, :, :, :, -2]
        gx /= (grid0.dlon * dx * meteva.base.dis_1_degree * 1000)

    gy = np.zeros(v.values.shape)
    gy[:, :, :, :, 1:-1, :] = (v.values[:, :, :, :, 2:, :] - v.values[:, :, :, :, :-2, :]) / 2
    gy[:, :, :, :, 0, :] = v.values[:, :, :, :, 1, :] - v.values[:, :, :, :, 0, :]
    gy[:, :, :, :, -1, :] = v.values[:, :, :, :, -1, :] - v.values[:, :, :, :, -2, :]
    gy /= (grid0.dlat * meteva.base.dis_1_degree * 1000)

    div = gx + gy

    div_grd = meteva.base.grid_data(grid0, div)

    return div_grd


def uv_to_vor(u, v):
    lats = u["lat"].values
    lons = u["lon"].values
    xx, yy = np.meshgrid(lons, lats)
    dx = np.cos(yy * math.pi / 180)
    grid0 = meteva.base.get_grid_of_data(u)
    if (grid0.dlon * grid0.nlon >= 360):
        gx = np.zeros(u.values.shape)
        gx[:, :, :, :, :, 1:-1] = (v.values[:, :, :, :, :, 2:] - v.values[:, :, :, :, :, :-2]) / 2
        gx[:, :, :, :, :, 0] = (v.values[:, :, :, :, :, 1] - v.values[:, :, :, :, :, -1]) / 2
        gx[:, :, :, :, :, -1] = (v.values[:, :, :, :, :, 0] - v.values[:, :, :, :, :, -2]) / 2
        gx /= (grid0.dlon * dx * meteva.base.dis_1_degree * 1000)
    else:
        gx = np.zeros(u.values.shape)
        gx[:, :, :, :, :, 1:-1] = (v.values[:, :, :, :, :, 2:] - v.values[:, :, :, :, :, :-2]) / 2
        gx[:, :, :, :, :, 0] = v.values[:, :, :, :, :, 1] - v.values[:, :, :, :, :, 0]
        gx[:, :, :, :, :, -1] = v.values[:, :, :, :, :, -1] - v.values[:, :, :, :, :, -2]
        gx /= (grid0.dlon * dx * meteva.base.dis_1_degree * 1000)

    gy = np.zeros(v.values.shape)
    gy[:, :, :, :, 1:-1, :] = (u.values[:, :, :, :, 2:, :] - u.values[:, :, :, :, :-2, :]) / 2
    gy[:, :, :, :, 0, :] = u.values[:, :, :, :, 1, :] - u.values[:, :, :, :, 0, :]
    gy[:, :, :, :, -1, :] = u.values[:, :, :, :, -1, :] - u.values[:, :, :, :, -2, :]
    gy /= (grid0.dlat * meteva.base.dis_1_degree * 1000)

    vor = gx  - gy
    vor_grd = meteva.base.grid_data(grid0, vor)
    return vor_grd



def t_to_ro(t):
    p = t["level"].values[0]
    ro = p * 28.97 / (8.314 * t.values * 1000)
    grid0 = meteva.base.get_grid_of_data(t)
    ro_grd = meteva.base.grid_data(grid0, ro)
    return ro_grd


def uvtq_to_mfd(u, v, t, q):
    ro = t_to_ro(t)
    uqro = u.copy()
    uqro.values *= (q.values * ro.values)
    vqro = v.copy()
    vqro.values *= (q.values * ro.values)

    div = uv_to_div(uqro, vqro)
    div.values *= 1000000
    return div