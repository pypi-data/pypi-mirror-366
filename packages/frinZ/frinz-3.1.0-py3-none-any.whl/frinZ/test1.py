import cor
import numpy as np
import matplotlib.pyplot as plt



ifile = "../data/YAMAGU34_HITACH32_2023262102100_all.cor"
header = cor.header(ifile)
print(header)

visibility = cor.visibility(ifile, skip=0, delay=0, rate=0.0, header=header)
print(visibility)

spectrum = cor.frinZspectrum(visibility,length=header["PP"], loop=0, header=header)
print(spectrum)

search = cor.frinZsearch(spectrum, fft_point=header["FFT"])
print(search)

frequency = cor.frequency(fft_point=header["FFT"], bw=int(header["Sampling-frequency-MHz"]/2))
rate = cor.rate(fft_point=header["FFT"], effective_integration_length=visibility[2])
delay = cor.delay(fft_point=header["FFT"])

param = cor.frinZparam(lag_rate_2D_array=search, 
                       delay_win=[-10,30],
                       rate_win=[-0.1, 0.1], header=header, effective_integration_length=visibility[2])
print(param)

plt.plot(delay, param["delay_list"])
plt.show()


cor.frinZplot(frequency, rate, visibility[0], show=True, type="vis", flag="phase")
