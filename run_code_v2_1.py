import os
os.environ["OMP_NUM_THREADS"] = "6"
os.environ["MKL_NUM_THREADS"] = "6"
os.environ["NUMEXPR_NUM_THREADS"] = "6"
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import netCDF4 as nc
import cartopy.crs as ccrs
from sklearn.linear_model import LinearRegression
from scipy.signal import detrend
from scipy.stats import linregress
import scipy.stats as st
# 
i_part = 0
n_ms = 31               #number of moving sum (+- 15 plus itself)
# setting variable, areas of interests
lon_min, lon_max = 60 * i_part - 180, 60 * i_part - 120
lat_min, lat_max = -90, 90
variable = 'mtpr'       # total flux preipitation (kg/m^2/s)

D = nc.Dataset('/work5/ERA5_daily_landgrid_only/global/compressed_sfc_fc_daily_197901.nc4')
lon = np.array(D.variables['lon'])
lon[lon > 180] = lon[ lon > 180] - 360
lat = np.array(D.variables['lat'])
if i_part == 5:                                                             # When i_part == 5, include lon == 180
        mask = (lon >= lon_min) & (lon <= lon_max) & (lat >= lat_min) & (lat <= lat_max)
else:
    mask = (lon >= lon_min) & (lon < lon_max) & (lat >= lat_min) & (lat <= lat_max) 

grid_lons = lon[mask]
grid_lats = lat[mask]
n_grid = len(grid_lats)

del lon, lat, mask, D

file_to_load = '/work/home/L.b09209035/whiplash/era5_mtpr_data/original_mtpr_v1/ERA5_mtpr_part_{:d}.npz'.format(i_part+1)
myvar = np.load(file_to_load)['arr_0']
#np.savez_compressed('north_africa.npz', myvar)
print('variable loading finished')

##################
print('start to detrend')
date_strings = pd.date_range(start='1980-01-01', end = '1980-12-31', freq='D')
date_strings = date_strings.strftime('%m/%d')
date_strings
date_mapping = dict(zip(date_strings, np.arange(1, 367))) 

Days = pd.date_range(start="1979-01-01", end="2019-12-31", freq="D")                # 1979~2019
def detrend_and_define_extreme(ary, upper_q, lower_q):  
    global lower_thres, upper_thres
    D = pd.DataFrame({'Time': Days, 'raw data': ary})   
    D['year'] = D['Time'].dt.year
    D['date'] = D['Time'].dt.strftime('%m/%d')
    #mask_229 = D['Time'].dt.strftime('%m%d') == '0229'
    #mask_229 = mask_229[mask_229].index
    #mask_229
    #D = D.drop(index = mask_229).reset_index(drop = True)
    scaling = 1000000
    D['scaled raw data'] = D['raw data'] * scaling                     # scaling = 1000 to avoid floating

    #D['DoY'] = D['Time'].dt.day_of_year
    #print(D)
    global annaul_mean

    annaul_mean = np.array( D[['scaled raw data', 'year']].groupby('year').mean(), dtype = np.float64 )[:, 0]
    mapping = dict(zip(np.unique(D['year']), annaul_mean))
    D['scaled annual mean'] = D['year'].map(mapping)

    SLR = linregress(np.arange(1979, 2020, 1), annaul_mean)                         # 1979~2019
    slope = SLR.slope
    intercept = SLR.intercept
    #plt.plot(annaul_mean)
    #plt.title('ammual mean mtpr')
    #print('annual trend of mtpr', slope)
    def trend(year, slope, intercept):
        y = slope * year + intercept
        return y
    D['scaled year trend'] = trend(np.array(D['year']), slope, intercept)
    #D['scaled detrended resi'] = D['scaled raw data'] - D['scaled year trend']
    D['scaled data detrended'] = D['scaled raw data'] - D['scaled year trend']
    #D['scaled data detrended'] = (D['scaled detrended resi'] + D['scaled annual mean']  )

   
    n_add = int(0.5*(n_ms - 1))
    var_moving_sum_30 = np.convolve(D['scaled data detrended'], np.ones(n_ms), 'valid')

    var_moving_sum_30 = np.insert(var_moving_sum_30, 0, [np.nan for i in range(n_add)])
    var_moving_sum_30 = np.append(var_moving_sum_30, [np.nan for i in range(n_add)])

    D['scaled data 30 days sum'] = var_moving_sum_30

    D_pivot = pd.pivot_table(D, values = 'scaled data 30 days sum', columns = 'year', index = 'date')
    #print('pivot shape = ', D_pivot.shape)
    D_extreme = D_pivot.copy()
    D_extreme.iloc[:, :] = 0
    D_standardized = D_pivot.copy()
    D_standardized.iloc[:, :] = 0
    
    margin_q = 0
    upper_q = np.round( upper_q - margin_q, 2)
    lower_q = np.round( lower_q + margin_q, 2)
    #print(upper_q, lower_q)
    THRE_daily = dict()

    for i in range(366):
        mean = np.nanmean(D_pivot.iloc[i, :])
        std = np.nanstd(D_pivot.iloc[i, :])
        D_standardized.iloc[i, :] = (D_pivot.iloc[i, :] - mean) / std
        lower_thres = np.nanpercentile( D_standardized.iloc[i, :], lower_q * 100)
        upper_thres = np.nanpercentile( D_standardized.iloc[i, :], upper_q * 100)
        THRE_daily[i+1] = (lower_thres, upper_thres)
        
        mask_lower = D_standardized.iloc[i,:] <= lower_thres
        mask_upper = D_standardized.iloc[i,:] >= upper_thres
        D_extreme.iloc[i, :][mask_lower] = -1
        D_extreme.iloc[i, :][mask_upper] = 1
        

    D_standardized = D_standardized.reset_index().melt(id_vars='date')
    to_delete = (D_standardized['date'] == '02/29') & ( np.isnan(D_standardized['value'] ) )            # deleteing 02/29 dats that are not in leap year
    to_delete = to_delete[to_delete].index
    D_standardized = D_standardized.drop(index=to_delete).reset_index(drop = True)
    D_extreme = D_extreme.reset_index().melt(id_vars='date')
    D_extreme = D_extreme.drop(index=to_delete).reset_index(drop = True)

    D['scaled standardized summation'] = D_standardized['value']
    D['standardized summation'] = D['scaled standardized summation'] / scaling
    D['rough extreme event'] = D_extreme['value']

    
    D['date map'] = D['date'].map(date_mapping)
    D['scaled daily thres'] = D['date map'].map(THRE_daily)   

    return D

def get_rough_extremes(DRY_or_Wet_time_index_array):
    rough_extremes = dict()
    E = DRY_or_Wet_time_index_array
    E = np.append(E, 999999)                # append to deal with the last event
    t0 = E[0]
    cumulative_period = 1
    for i in range(1, len(E)):
        t = E[i]
        if t - t0 == 1:
            cumulative_period += 1

        else:
            rough_extremes[t0 - cumulative_period + 1] = cumulative_period          # save start and duration of rough events
            cumulative_period = 1
        t0 = t
    E = E[:-1]
    return rough_extremes

def identify_whiplash(DF, DRY_rough_dict, WET_rough_dict, min_period, min_duration, inter_period):

    # step 1: to merge same extreme
    def merge_event(DF, event_dict, min_period, ex_type):
        if ex_type == 'DRY':
            ex = 0
        elif ex_type == 'WET':
            ex = 1
        else:
            print('error')
            
        events = sorted([(s, s+d-1) for s, d in event_dict.items()])
        merged = []
        merge_count = 0
        for start, end in events:
            if not merged:
                merged.append([start, end])
            else:
                prev_start, prev_end = merged[-1]
                if start - prev_end <= min_period:  # merge close events
                    #m_thre = DF['scaled daily thres'][prev_start][ex]
                    mean = np.nanmean( DF['scaled standardized summation'][prev_start: start])
                    
                    if ex_type == 'DRY':
                        if mean <= lower_thres:
                            merge_count += 1
                            merged[-1][1] = max(prev_end, end)
                        else:
                            merged.append([start, end])
                    elif ex_type == 'WET':
                        if mean >= upper_thres:
                            merge_count += 1
                            merged[-1][1] = max(prev_end, end)
                        else:
                            merged.append([start, end])
                            
                else:
                    merged.append([start, end])
        return merged

    Indep_DRY = merge_event(DF, DRY_rough_dict, min_period=min_period, ex_type='DRY')
    Indep_WET = merge_event(DF, WET_rough_dict, min_period=min_period, ex_type='WET')
    # step 2: to delete events that are too short 
    Indep_DRY = [(s, e) for s, e in Indep_DRY if (e - s + 1) >= min_duration]
    Indep_WET = [(s, e) for s, e in Indep_WET if (e - s + 1) >= min_duration]
    # step 3: to identify Whilpash
    whiplash_dw = []
    for d_start, d_end in Indep_DRY:
        for w_start, w_end in Indep_WET:
            if 0 < (w_start - d_end) <= inter_period:
                if len(whiplash_dw) > 0 and  whiplash_dw[-1][2:] == (w_start, w_end):               # avoid repetitive counting
                    del whiplash_dw[-1]
                    
                whiplash_dw.append((d_start, d_end, w_start, w_end))
                break

    whiplash_wd = []
    for w_start, w_end in Indep_WET:
        for d_start, d_end in Indep_DRY:
            if 0 < (d_start - w_end) <= inter_period:
                if len(whiplash_wd) > 0 and whiplash_wd[-1][2:] == (d_start, d_end):                # avoid repetitive counting
                    del whiplash_wd[-1]

                whiplash_wd.append((w_start, w_end, d_start, d_end))
                break

    return whiplash_dw, whiplash_wd



filename_DW_s = 'Dry_to_Wet_stats_part_{:d}.txt'.format(i_part+1)
filename_WD_s = 'Wet_to_Dry_stats_part_{:d}.txt'.format(i_part+1)

min_period = 30
min_duration = 3
inter_period = 30

upper_q = 0.9
lower_q = 0.1
DW_stats = []
WD_stats = []

format_out = '%.2f'
def summary():
    print('#######################')
    print('AREA')
    print('lon: {}~{}'.format(lon_min, lon_max))
    print('lat: {}~{}'.format(lat_min, lat_max))
    print('In total, {} grids'.format(n_grid))

    print('#######################')
    print('METHODOLOGY')
    print('min_period, min_duration, inter_period: {}, {}, {}'.format(min_period, min_duration, inter_period))
    print('thresholds: {}, {}; margin: {}'.format(upper_q, lower_q, 0))
    print('moving sum of vairables before calculating whiplash:', int(n_ms - 1))

    print('#######################')
    print('filename to save: {}, {}'.format(filename_DW_s, filename_WD_s))
    print('outputted size: 69. (41 years count, 12 month counts, 7 first ex stats, 2 transit stats, 7 second ex stats)')
    print('output format: ', format_out)
    print('#######################\n')
    return
summary()





def plot_daily_standardized_TS(D, i_start, i_end, upper_q, lower_q, var_name):
    d_xticks = int( (i_end - i_start) / 6 )
    z_lower = st.norm.ppf(lower_q)                              # normal approzimation
    z_upper = st.norm.ppf(upper_q)
    plt.ylim([-2,2])
    #plt.plot(D['Time'][i_start: i_end], D['scaled standardized summation'][i_start:i_end], color = 'black')
    plt.plot( D['scaled standardized summation'][i_start:i_end], color = 'black')
    #plt.xticks(D['Time'][i_start: i_end][::d_xticks], fontsize = 7)
    plt.axhline(y = z_lower, color = 'darkorange', linestyle = '--')
    plt.axhline(y = z_upper, color = 'darkgreen', linestyle = '--')
    title_text = 'daily standardized {:s} time series data'.format(var_name)
    plt.title(title_text)
    plt.show()
    return





Days_df = pd.DataFrame(Days, columns=['date'])

def whiplash_counts_stats(whi: list) -> list:
    n_whi = len(whi)
    whi_start_index = [whi[i][0] for i in range(n_whi)]     # index of start of the whiplash(dw or wd)
    whi_start_year = Days_df.iloc[whi_start_index, 0].dt.year.tolist()
    whi_start_month = Days_df.iloc[whi_start_index, 0].dt.month.tolist()
    
    whi_first_ex = [whi[i][1] - whi[i][0] + 1 for i in range(n_whi)]   # duration of first extreme event of the whiplash(dw or wd)
    whi_transition = [whi[i][2] - whi[i][1] - 1 for i in range(n_whi)]
    whi_second_ex = [whi[i][3] - whi[i][2] + 1 for i in range(n_whi)]  # duration of second extreme event of the whiplash(dw or wd)
    #whi_druation = [whi[i][3] - whi[i][0] for i in range(n_whi)]
    
    return whi_start_year, whi_start_month, whi_first_ex, whi_transition, whi_second_ex

def stats_to_output(whi_year, whi_month, whi_first_ex, whi_transition, whi_second_ex):
    n_years = 41
    year_counts = np.zeros(n_years)
    month_counts = np.zeros(12)
    for i in range(len(whi_year)):
        year_counts[whi_year[i]-1979] += 1
        month_counts[whi_month[i] - 1] += 1

    def stats_for_extremes(whi_ex):
        m, s = np.mean(whi_ex), np.std(whi_ex)
        med, IQR = np.median(whi_ex), np.percentile(whi_ex, 75) - np.percentile(whi_ex, 25)
        try:
            k, loc, th = st.gamma.fit(whi_ex, floc=0) 
            ks = st.kstest(whi_ex, 'gamma', args=(k, loc, th))
            ks_pvalue = ks.pvalue

        except Exception as e:
            k, loc, th = -1,-1, -1                      # -1 as nan value
            ks_pvalue = -1

        return m, s, med, IQR, k, th, ks_pvalue         # return mean, std, median, IQR, gamma(shape, scale), pvalue of K-S test
    
   
    first_ex_stats = stats_for_extremes(whi_first_ex)
    second_ex_stats = stats_for_extremes(whi_second_ex)
    transi_ave = np.mean(whi_transition)
    transi_std = np.std(whi_transition)

    output_array = np.hstack((year_counts, month_counts, first_ex_stats, transi_ave,transi_std,second_ex_stats))
    
    return output_array     # output size: 69 = 41+12+7+2+7




print('start to loop for each grid')
for z in range(n_grid):
#for z in range(10):
    if z % 100 == 0:
        print('loops {:d}th of out {:d}'.format(z, n_grid))
        np.savetxt(filename_DW_s, DW_stats, fmt = format_out)
        np.savetxt(filename_WD_s, WD_stats, fmt = format_out)
    df_z = detrend_and_define_extreme(myvar[:, z], upper_q=upper_q, lower_q=lower_q)
    DRY = (df_z['rough extreme event'] == -1)
    DRY = np.array(DRY[DRY].index)
    WET = (df_z['rough extreme event'] == 1)
    WET = np.array(WET[WET].index)

    DRY_rough_dict = get_rough_extremes(DRY)
    WET_rough_dict = get_rough_extremes(WET)

    dw, wd = identify_whiplash(DF = df_z, DRY_rough_dict=DRY_rough_dict, WET_rough_dict=WET_rough_dict,
                               min_period=min_period, min_duration=min_duration, inter_period=inter_period )
    if len(dw) == 0:
        print('empty dw at z = {:d}'.format(z))
        DW_stats.append(np.ones(69)*(-1))       # 69 is the output size of my stats, -1 as nan value
    else:
        Whi_year, Whi_month, Whi_first_ex, Whi_transition, Whi_second_ex = whiplash_counts_stats(dw)
        output_array = stats_to_output(Whi_year, Whi_month, Whi_first_ex, Whi_transition, Whi_second_ex)
        DW_stats.append(output_array)

    if len(wd) == 0:
        print('empty wd at z = {:d}'.format(z))
        WD_stats.append(np.ones(69)*(-1))
    else:
        Whi_year, Whi_month, Whi_first_ex, Whi_transition, Whi_second_ex = whiplash_counts_stats(wd)
        output_array = stats_to_output(Whi_year, Whi_month, Whi_first_ex, Whi_transition, Whi_second_ex)
        WD_stats.append(output_array)

np.savetxt(filename_DW_s, DW_stats, fmt = format_out)
np.savetxt(filename_WD_s, WD_stats, fmt = format_out)
