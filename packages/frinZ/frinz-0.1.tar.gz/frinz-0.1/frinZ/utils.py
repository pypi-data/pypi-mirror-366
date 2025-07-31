

import os
import sys
import datetime
import numpy as np
import scipy.fft
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import matplotlib
matplotlib.style.use('fast')
#matplotlib.use("Agg")
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time



def zerofill(integ: int) -> int :
    powers_of_two = 1
    integ_re      = integ
    while True :
        powers_of_two = powers_of_two * 2
        integ = integ / 2
        if integ < 1.0 :
            break
        else :
            continue
    zero_num = int(powers_of_two - integ_re)
    return powers_of_two, zero_num

def RFI(r0, bw: int, fft: int) -> int :
    # RFI
    rfi_cut_min = []
    rfi_cut_max = []
    for r1 in r0 :
        rfi_range = r1.split(",")
        rfi_min = int(rfi_range[0])
        rfi_max = int(rfi_range[1])
        if rfi_max > 512 :
            rfi_max = 512
        if rfi_min < 0 or rfi_max < 0 :
            print("The RFI minimum, %.0f, or maximum, %.0f, frequency is more than 0." % (rfi_min, rfi_max))
            exit(1)
        elif rfi_min >= rfi_max :
            print("The RFI maximum frequency, %.0f, is smaller than the RFI minimum frequency, %.0f." % (rfi_min, rfi_max))
            exit(1)
        else :
            pass

        r2 = int(rfi_min) * int(fft/2/bw); rfi_cut_min.append(r2)
        r3 = int(rfi_max) * int(fft/2/bw); rfi_cut_max.append(r3)
        
    return rfi_cut_min, rfi_cut_max, len(r0)


def noise_level(input_2D_data: float, search_00_amp: float, flag: str) -> float :
    
    if flag == "frequency" :
        non_zero_data  = (input_2D_data > 0+0*1j)
        input_2D_data  = input_2D_data[non_zero_data]

    input_2D_data -= np.mean(input_2D_data) # 複素数でも実部と虚部でそれぞれで平均を計算できるみたい．

    if flag == "time" :
        noise_level = np.mean(np.absolute(input_2D_data))
        #noise_level = np.std(np.absolute(input_2D_data)) # 信号の平均値が直流成分に対応するため，それを除去のために平均値を引いている？．加算平均をとることで雑音レベルを下げることができるらしい．
    if flag == "frequency" :
        noise_level = np.absolute(input_2D_data)
        noise_level = noise_level[noise_level<=np.std(noise_level)]
        noise_level = np.mean(noise_level)

    try :
        SNR = search_00_amp / noise_level
    except ZeroDivisionError :
        SNR, noise_level  = 0.0, 0.0

    return SNR, noise_level




exit()

# label
label = os.path.splitext(ifile)[0].split("_")[-1]





cumulate_len, cumulate_snr, cumulate_noise = [], [], []
add_plot_length, add_plot_amp, add_plot_snr, add_plot_phase, add_plot_noise_level = [], [], [], [], []
for l in range(loop) :

    # the cumulation of the integration time.
    if cumulate != 0 :
        if length <= PP :
            length += cumulate
            l = 0
    if length > PP : # for --cumulate
        break

    # epoch
    epoch0 = obs_scan_time[length*l:length*(l+1)]
    epoch0 = datetime.datetime(1970,1,1,0,0,0) + datetime.timedelta(seconds=epoch0[0])
    epoch1 = epoch0.strftime("%Y/%j %H:%M:%S")
    epoch2 = epoch0.strftime("%Y%j%H%M%S")
    epoch3 = epoch0.strftime("%Y-%m-%d %H:%M:%S")


    mjd = "%.5f" % Time("T".join(epoch3.split()), format="isot", scale="utc").mjd

    # azel 
    station1_azel = RaDec2AltAz(source_position_ra, source_position_dec, epoch3, station1_position_x, station1_position_y, station1_position_z)
    station2_azel = RaDec2AltAz(source_position_ra, source_position_dec, epoch3, station2_position_x, station2_position_y, station2_position_z)


    #
    # IFFT & FFT
    #
    integ_fft = 4 *zerofill(integ=length)[0] # the FFT in the time (same as integration time) direction. rate

    #
    # RFI cut
    #
    if rfi != False :
        rfi_cut_min, rfi_cut_max, rfi_num = RFI(r0=rfi, bw=BW, fft=fft_point)
        for i in range(rfi_num) :
            for r in range(rfi_cut_min[i], rfi_cut_max[i]+1) :
                if r >= int(fft_point/2) :
                    continue
                complex_visibility_split[:,r] = 0+0j

    # Scipy version
    freq_rate_2D_array = np.fft.fftshift(scipy.fft.fft(complex_visibility_split, axis=0, n=integ_fft, workers=cpu), axes=0) * fft_point / length


    fringe_freq_rate_00_complex_index = np.where(rate_range==yi_freq_rate)[0][0]

        

    lag_rate_2D_array  = np.fft.ifftshift(scipy.fft.ifft(freq_rate_2D_array, axis=1, n=fft_point, workers=cpu), axes=1)
    lag_rate_2D_array  = lag_rate_2D_array[:, ::-1]        # 列反転，これは delay が０を中心に対称になるため．


    #
    # fringe search
    #
    # frequency domain
    if freq_plot == True :

        fringe_freq_rate_00_spectrum      = freq_rate_2D_array[fringe_freq_rate_00_complex_index,:]
        fringe_freq_rate_00_amplitude1    = np.absolute(fringe_freq_rate_00_spectrum)
        fringe_freq_rate_00_phase1        = np.angle(fringe_freq_rate_00_spectrum, deg=True)
        fringe_freq_rate_00_index         = fringe_freq_rate_00_amplitude1.argmax()
        fringe_freq_rate_00_amp           = fringe_freq_rate_00_amplitude1[fringe_freq_rate_00_index]
        fringe_freq_rate_00_freq          = freq_range[fringe_freq_rate_00_index]
        fringe_freq_rate_00_rate          = np.absolute(freq_rate_2D_array[:,fringe_freq_rate_00_index])
        fringe_freq_rate_00_phase2        = fringe_freq_rate_00_phase1[fringe_freq_rate_00_index]

        #
        # noise level, frequency domain
        #
        SNR_freq_rate, noise_level_freq = noise_level(freq_rate_2D_array, fringe_freq_rate_00_amp, "frequency")
    

    if freq_plot != True :
        
        #
        # When the target flux density is nearly detection limit in VLBI
        #
        if delay_win != False and rate_win != False :
            delay_win_range_low = float(delay_window_low)
            delay_win_range_high = float(delay_window_high)
            rate_win_range_low = float(rate_window_low)
            rate_win_range_high = float(rate_window_high)
            delay_win_range = (float(delay_window_low) <= lag_range)  & (lag_range <= float(delay_window_high))
            rate_win_range  = (float(rate_window_low)  <= rate_range) & (rate_range <= float(rate_window_high))
            delay_rate_fringe_search_area = lag_rate_2D_array[rate_win_range][:,delay_win_range]
            delay_win_range_max_idx, rate_win_range_max_idx = np.unravel_index(np.argmax(np.absolute(delay_rate_fringe_search_area)), delay_rate_fringe_search_area.shape)
            yi_time_rate = lag_range[delay_win_range][rate_win_range_max_idx]
            yi_time_lag  = rate_range[rate_win_range][delay_win_range_max_idx]
        elif delay_win == False and rate_win == False :
            pass
        else :
            print("You should select the option of the both \"--delay-window\" and \"--rate-window\"!!")
            quit()
            
        fringe_lag_rate_00_complex_index1 = np.where(rate_range==yi_time_lag )[0][0] # the direction of the lag
        fringe_lag_rate_00_complex_index2 = np.where(lag_range ==yi_time_rate)[0][0] # the direction of the rate
        fringe_lag_rate_00_lag            = np.absolute(lag_rate_2D_array[fringe_lag_rate_00_complex_index1])
        fringe_lag_rate_00_rate           = np.absolute(lag_rate_2D_array[:,fringe_lag_rate_00_complex_index2])
        fringe_lag_rate_00_amp            = np.absolute(lag_rate_2D_array[fringe_lag_rate_00_complex_index1,fringe_lag_rate_00_complex_index2])
        fringe_lag_rate_00_phase          = np.angle(lag_rate_2D_array[fringe_lag_rate_00_complex_index1,fringe_lag_rate_00_complex_index2], deg=True)

        #
        # noise level, time domain
        #
        SNR_time_lag, noise_level_lag = noise_level(lag_rate_2D_array, fringe_lag_rate_00_amp, "time")

    #
    # fringe output
    #
    if freq_plot == True : # cross-soectrum
        if l == 0 :
            ofile_name_freq = F"{save_file_name}_freq.txt"
            output_freq  = F"#******************************************************************************************************************************************************************************************\n"
            output_freq += F"#      Epoch        Label    Source      Length     Amp       SNR      Phase     Frequency     Noise-level           {station1_name}-azel               {station2_name}-azel             MJD        Bandpass\n"
            output_freq += F"#year/doy hh:mm:ss                        [s]       [%]                [deg]       [MHz]       1-sigma [%]   az[deg]  el[deg]  height[m]   az[deg]   el[deg]  height[m]          \n"
            output_freq += F"#******************************************************************************************************************************************************************************************"
            print(output_freq); output_freq += "\n"
        output1 = "%s    %s    %s     %.3f     %f %7.1f  %+8.3f    %8.3f      %f       %.3f  %.3f  %.3f       %.3f  %.3f  %.3f   %s   %s" % \
            (epoch1, label, source_name, length*effective_integration_length, fringe_freq_rate_00_amp*100, SNR_freq_rate, fringe_freq_rate_00_phase2, fringe_freq_rate_00_freq, noise_level_freq*100, \
             station1_azel[0], station1_azel[1], station1_azel[2], station2_azel[0], station2_azel[1], station2_azel[2], mjd, bandpass_flag)
        output_freq += "%s\n" % output1; print(output1)

        if spectrum :
            if l == 0 : spectrum_dict = {}; spectrum_ofile = f"{spectrum_path}/{save_file_name}.npz"
            spectrum_dict[epoch2] = fringe_freq_rate_00_spectrum
            if l == loop-1 : np.savez_compressed(spectrum_ofile, **spectrum_dict)

    if freq_plot != True : # fringe
        if l == 0 :
            ofile_name_time = F"{save_file_name}_time.txt"
            output_time  = F"#*****************************************************************************************************************************************************************************************************************************\n"
            output_time += F"#      Epoch         Label     Source      Length      Amp        SNR     Phase     Noise-level      Res-Delay     Res-Rate            {station1_name}-azel               {station2_name}-azel              MJD       Bandpass\n"
            output_time += F"#year/doy hh:mm:ss                          [s]        [%]                [deg]     1-sigma[%]       [sample]        [Hz]      az[deg]  el[deg]  height[m]   az[deg]   el[deg]  height[m]                                     \n"
            output_time += F"#*****************************************************************************************************************************************************************************************************************************"
            print(output_time); output_time += "\n"
        output2 = "%s    %s   %s     %.3f     %.6f  %7.1f  %+8.3f     %f    %+.2f     %+f     %.3f  %.3f  %.3f      %.3f  %.3f  %.3f   %s   %s" % \
            (epoch1, label, source_name, length*effective_integration_length, fringe_lag_rate_00_amp*100, SNR_time_lag, fringe_lag_rate_00_phase, noise_level_lag*100, yi_time_rate, yi_time_lag, \
             station1_azel[0], station1_azel[1], station1_azel[2], station2_azel[0], station2_azel[1], station2_azel[2], mjd, bandpass_flag)
        output_time += "%s\n" % output2; print(output2)

