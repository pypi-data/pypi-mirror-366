import frinZ
import matplotlib.pyplot as plt



ifile = "/home/akimoto/program/python/frinZ-pypi/data/YAMAGU34_HITACH32_2023262102100_all.cor"

header = frinZ.cor.header(ifile)

visibility = frinZ.cor.visibility(ifile, skip=0, delay=0, rate=0.0, header=header)

length = 10
for i in range(int(header["PP"]/length)) :

    spectrum = frinZ.cor.frinZspectrum(visibility,length=length, loop=i, header=header)

    #spectrum = frinZ.cor.frinZspectrum(visibility,length=header["PP"], loop=0, header=header)

    search = frinZ.cor.frinZsearch(spectrum, fft_point=header["FFT"])

    frequency = frinZ.cor.frequency(fft_point=header["FFT"], bw=int(header["Sampling-frequency-MHz"]/2))
    rate = frinZ.cor.rate(length, effective_integration_length=visibility[2])
    delay = frinZ.cor.delay(fft_point=header["FFT"])

    param = frinZ.cor.frinZparam(lag_rate_2D_array=search, 
                        delay_win=[-10,30],
                        rate_win=[-0.1,0.1],
                         length=length,
                         header=header, 
                         effective_integration_length=visibility[2])
    
    print(spectrum[0][1], param["fringe_amp"], param['fringe_phase'], param['res_delay'], param['res_rate'],param['snr'], param["noise"])
    frinZ.cor.frinZplot(delay, rate, search, show=True, type="time", flag="amp")