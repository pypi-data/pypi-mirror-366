import numpy as np
from numpy import *
from scipy.spatial.distance import jensenshannon
import meteva
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cmaps


def mulde_array(obs_origin, fst_origin, floor=0.1, levels=50):
    # obs,fst should all be type of 2D ma.array

    # print(obs_origin)
    # print(fst_origin)
    # print("*********")

    obs = list(filter(lambda x: x >= floor, obs_origin.ravel()))
    fst = list(filter(lambda x: x >= floor, fst_origin.ravel()))

    if(len(obs)==0) and len(fst)==0:
        return np.nan,np.nan,np.nan,np.nan
    R_o = sum(obs)
    R_f = sum(fst)
    maxval = ma.where(R_f >= R_o, R_f, R_o) + 1e-8
    ET = (R_f - R_o) / maxval

    # sum of rain area (by num of precipitation grids)
    S_o = (obs_origin >= max(floor, 0.1)).sum()
    S_f = (fst_origin >= max(floor, 0.1)).sum()
    maxval = ma.where(S_f >= S_o, S_f, S_o) + 1e-8
    EA = (S_f - S_o) / maxval

    if len(obs) == 0 and len(fst) != 0:
        ES = 1
        E = (abs(ET) + abs(EA) + ES) / 3
        return E, ET, EA, ES
    if len(obs) != 0 and len(fst) == 0:
        ES = 1
        E = (abs(ET) + abs(EA) + ES) / 3
        return E, ET, EA, ES
    if len(obs) != 0 and len(fst) == 0:
        ES = 0
        ET = 0
        EA = 0
        E = 0
        return E, ET, EA, ES

    ##bins_norm=linspace(0,1,levels+1)
    obs_norm = obs / (quantile(obs, 0.95) + 1e-4)
    hist, bins = histogram(obs_norm.ravel(), bins=levels)
    pdf_o = hist / hist.sum()  # it equals f(x)dx

    fst_norm = fst / (quantile(fst, 0.95) + 1e-4)
    hist, bins = histogram(fst_norm.ravel(), bins=levels)
    pdf_f = hist / hist.sum()  # it equals f(x)dx

    ES = jensenshannon(pdf_f, pdf_o)
    ES = ES ** (0.5)  # EH is too small, make it big but still in [0,1]

    E = (abs(ET) + abs(EA) + ES) / 3
    ##print(f"floor is {floor:.4f}, E is {E:.4f},ET is {ET:.4f}, EA is {EA:.4f},ES is {ES:.4f}")

    return E, ET, EA, ES




def mulde_xy(grd_ob,grd_fo,floor = 0.1,levels = 50,half_window_size = 1,save_path = None,show = False,
           width = 10,height = None,wspace = 1,hspace = 0.5,
          sup_fontsize = 12):
    '''
    本模块的作用是根据输入的实况和预报平面场数据，统计pbs的空间分布情况

    :param grd_ob: 实况的网格数据
    :param grd_fo:  预报的网格数据
    :param floor:  最小的降水阈值，小于该阈值的要素会被置为0，不参与检验
    :param levels:  计算气象要素空间分布概率密度函数时的步数，默认为50
    :param half_window_size: 半窗口大小，窗口大小=half_window_size*2 + 1
    :return:
    '''
    grid0 = meteva.base.get_grid_of_data(grd_fo)
    E= np.zeros((grid0.nlat,grid0.nlon))
    ET=np.zeros((grid0.nlat,grid0.nlon))
    EA=np.zeros((grid0.nlat,grid0.nlon))
    ES=np.zeros((grid0.nlat,grid0.nlon))

    obs = grd_ob.values.squeeze()
    fst = grd_fo.values.squeeze()

    p = half_window_size
    for j in range(grid0.nlat):
        if j<p or j>grid0.nlat-p-1: continue
        for i in range(grid0.nlon):
            if i<p or i>grid0.nlon-p-1: continue
            py=min([p,j])
            px=min([p,i])
            obs_sub=obs[j-py:j+py+1,i-px:i+px+1]  #提取窗口内的观测
            fst_sub=fst[j-py:j+py+1,i-px:i+px+1]  #提取窗口内的预报
            E[j,i], ET[j,i], EA[j,i], ES[j,i] = mulde_array(obs_sub,fst_sub,floor,levels)  #调用pbs算法


    grd_E = meteva.base.grid_data(grid0,E)
    grd_ET = meteva.base.grid_data(grid0,ET)
    grd_EA = meteva.base.grid_data(grid0,EA)
    grd_ES = meteva.base.grid_data(grid0,ES)

    clevs0 = np.arange(0, 1.01, 0.1)
    clevs1 = np.arange(-1, 1.01, 0.1)
    #将结果绘制成图片
    if save_path is not None or show:

        cmap1 = cmaps.WhiteBlueGreenYellowRed


        time_str = meteva.base.all_type_time_to_str(grid0.gtime[0])
        dtime_str = str(grid0.dtimes[0]).zfill(3)
        win_str = "Win_len="+str(half_window_size*2+1)
        sup_title = time_str + "+" + dtime_str +" "+win_str
        axs = meteva.base.creat_axs(4,grid0,ncol=2,add_minmap=False,sup_title=sup_title,
                        wspace=wspace,hspace=hspace,width=width,height=height,
                                    add_index=["E","ET","ES","EA"],sup_fontsize = sup_fontsize)

        meteva.base.add_contourf(axs[0],grd_E,add_colorbar=True,
                                 cmap=cmap1,clevs=clevs0)

        meteva.base.add_contourf(axs[1],grd_ET,add_colorbar=True,
                                 cmap="RdBu_r",clevs=clevs1)

        meteva.base.add_contourf(axs[2],grd_ES,add_colorbar=True,
                                 cmap=cmap1,clevs=clevs0)

        meteva.base.add_contourf(axs[3],grd_EA,add_colorbar=True,
                                 cmap="RdBu_r",clevs=clevs1)

        if save_path is None:
            show = True
        else:
            plt.savefig(save_path,bbox_inches = "tight")

        if show:
            plt.show()

    return grd_E,grd_ET,grd_EA,grd_ES



if __name__=="__main__":
    import meteva.base as meb

    grid1 = meb.grid([100, 120, 0.1], [24, 40, 0.1])
    filename_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    filename_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(filename_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(filename_fo, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")

    result = mulde_xy(grd_ob,grd_fo,save_path=r"h:/a.png",show=False,sup_fontsize=12,floor=1)