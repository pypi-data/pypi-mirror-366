

import numpy as np

def Radian2RaDec(RA_radian: float, Dec_radian: float) -> float :
    Ra_deg  = np.rad2deg(RA_radian)
    Dec_deg = np.rad2deg(Dec_radian) 
    return Ra_deg, Dec_deg


def RaDec2AltAz(object_ra_deg: float, object_dec_deg: float, observation_time_datetime: float, latitude: float, longitude: float, height: float) -> float :
    
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz
    from astropy.time import Time
    from astropy import units as u
    
    location_geocentrice = EarthLocation.from_geocentric(latitude, longitude, height, unit=u.m)
    location_geodetic    = EarthLocation.to_geodetic(location_geocentrice)
    location_lon_lat     = EarthLocation(lon=location_geodetic.lon, lat=location_geodetic.lat, height=location_geodetic.height)
    obstime              = Time(F"{observation_time_datetime}")
    object_ra_dec        = SkyCoord(ra=object_ra_deg*u.deg, dec=object_dec_deg*u.deg)
    AltAz_coord          = AltAz(location=location_lon_lat, obstime=obstime)
    object_altaz         = object_ra_dec.transform_to(AltAz_coord)
    
    return object_altaz.az.deg, object_altaz.alt.deg, location_lon_lat.height.value

def header(ifile) :

    from collections import namedtuple

    header1 = np.fromfile(ifile, dtype="<i4", count=8).tolist()  # Software Version, Sampling Freq, FFT point, Number of Sector
    header2 = np.fromfile(ifile, dtype="<f8", count=32).tolist() # Station 1&2 XYZ position, Source Position, Clock Delay
    header3 = np.fromfile(ifile, dtype="<S8", count=17, offset=32).tolist() # Station Name, Station Code, Source Name
    header_field = ["version", "software", "sampling_speed", "fft", "sector", "frequency", 
                    "station1_posx", "station1_posy", "station1_posz", 
                    "station2_posx", "station2_posy", "station2_posz", 
                    "source_ra", "source_dec", 
                    "station1_delay", "station1_rate", "station1_acel", "station1_jerk", "station1_snap", 
                    "station2_delay", "station2_rate", "station2_acel", "station2_jerk", "station2_snap", 
                    "station1_name" , "station1_code", "station2_name", "station2_code", "source_name"]
    header = namedtuple("Header", header_field)
    header = header(header1[1], header1[2], header1[3], header1[6], header1[7], 
                    header2[2], header2[6], header2[7], header2[8], header2[12], header2[13], header2[14], header2[18], header2[19], 
                    header2[21], header2[22], header2[23], header2[24], header2[25], header2[27], header2[28], header2[29], header2[30], header2[31], 
                    header3[0].decode(), header3[5].decode(), header3[6].decode(), header3[11].decode(), header3[12].decode())

    magic_word          = "3ea2f983"
    header_version      = header.version
    software_version    = header.software
    sampling_speed      = header.sampling_speed / 10**6

    # FFT point, Number of Sector, observing frequency and parameter period
    fft_point           = header.fft
    number_of_sector    = header.sector
    observing_frequency = header.frequency/ 10**6
    PP  = number_of_sector         # parameter period
    BW  = int(sampling_speed // 2) # 
    RBW = BW / (fft_point // 2)    # resolution bandwidth

    # Station1
    station1_name       = header.station1_name
    station1_position_x = header.station1_posx
    station1_position_y = header.station1_posy
    station1_position_z = header.station1_posz
    station1_code       = header.station1_code

    # Station2
    station2_name       = header.station2_name
    station2_position_x = header.station2_posx
    station2_position_y = header.station2_posy
    station2_position_z = header.station2_posz
    station2_code       = header.station2_code

    # Source-Name
    source_name         = header.source_name
    source_position_ra, source_position_dec = Radian2RaDec(header.source_ra, header.source_dec)

    station1_clock_delay = header.station1_delay
    station1_clock_rate  = header.station1_rate
    station1_clock_acel  = header.station1_acel
    station1_clock_jerk  = header.station1_jerk
    station1_clock_snap  = header.station1_snap
    station2_clock_delay = header.station2_delay
    station2_clock_rate  = header.station2_rate
    station2_clock_acel  = header.station2_acel
    station2_clock_jerk  = header.station2_jerk
    station2_clock_snap  = header.station2_snap

    header_region_info = { 
        "Magic-Word":magic_word,
        "Sofrware-Vesion": software_version,
        "Header-Version": header_version,
        "Sampling-frequency-MHz": sampling_speed,
        "Observing-frequency-MHz": observing_frequency,
        "FFT": fft_point,
        "PP": number_of_sector,
        "BandWidth": BW,
        "Resolution BandWidth": RBW,
        "Station1-Name": station1_name,
        "Station1-Code": station1_code,
        "Station1-Clock-Delay": station1_clock_delay,
        "Station1-Clock-Rate ": station1_clock_rate,
        "Station1-Clock-Acel ": station1_clock_acel,
        "Station1-Clock-Jerk ": station1_clock_jerk,
        "Station1-Clock-Snap ": station1_clock_snap,
        "Station1-Pisition-XYZ": [station1_position_x, station1_position_y, station1_position_z],
        "Station2-Name": station2_name,
        "Station2-Code": station2_code,
        "Station2-Clock-Delay": station2_clock_delay,
        "Station2-Clock-Rate ": station2_clock_rate,
        "Station2-Clock-Acel ": station2_clock_acel,
        "Station2-Clock-Jerk ": station2_clock_jerk,
        "Station2-Clock-Snap ": station2_clock_snap,
        "Station2-Pisition-XYZ": [station2_position_x, station2_position_y, station2_position_z],
        "Source-Name": source_name,
        "Source-Position-RaDec": [source_position_ra, source_position_dec]
    }

    return header_region_info

def visibility(ifile, fft_point, skip, PP) :
    #
    # load cross-spectrum from the inputted cor-file
    #
    cor_file = open(ifile, "rb")
    complex_visibility = np.frombuffer(cor_file.read(), dtype="<f4", offset=256)
    complex_visibility = complex_visibility.reshape(PP, int(len(complex_visibility)/PP))
    effective_integration_length = complex_visibility[:,28][0]
    complex_visibility = np.delete(complex_visibility, np.linspace(0,33,34, dtype=int), 1)
    complex_visibility = np.insert(complex_visibility,0,0,axis=1)
    complex_visibility = np.insert(complex_visibility,1,0,axis=1)
    complex_visibility = complex_visibility.reshape(int(PP*(fft_point)/2), 2)
    complex_visibility = (complex_visibility[:,0] + complex_visibility[:,1] *1j).reshape(PP, int(fft_point/2))
    complex_visibility = complex_visibility[skip:]
    cor_file.close()

    cor_file = open(ifile, "rb")
    obs_scan_time = np.frombuffer(cor_file.read(), dtype="<i4", offset=256)
    obs_scan_time = obs_scan_time.reshape(PP, int(len(obs_scan_time)/PP))[:,0].tolist()
    obs_scan_time = obs_scan_time[skip:]
    cor_file.close()

    return complex_visibility, obs_scan_time, effective_integration_length

def delay(fft_point) :
    return np.linspace(-fft_point//2+1,fft_point//2,fft_point, dtype=int)  

def rate(fft_point, effective_integration_length) :
    return np.fft.fftshift(np.fft.fftfreq(fft_point, d=effective_integration_length))

def frequency(fft_point, BW) :
    return np.linspace(0, BW, fft_point//2)

def label(ifile) :
    import os 
    return os.path.splitext(ifile)[0].split("_")

"""
def frinZspectrum(visibility, fft_point, length, **kwargs) :

    import scipy

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

    delay = kwargs.get("delay", 0.0)
    rate  = kwargs.get("rate" , 0.0)
    skip  = kwargs.get("skip" , 0)
    PP    = kwargs.get("PP"   , 0)
    sampling_speed = kwargs.get("sampling_speed", 0)
    observing_frequency = kwargs.get("observing_frequency", 0)
    effective_integration_length = kwargs.get("effective_integration_length", 1)


    integ_fft = 4 *zerofill(integ=length)[0] # the FFT in the time (same as integration time) direction. rate


    if delay != 0 or rate != 0 :
        PP_correct = np.array([np.linspace(skip+1,PP,PP-skip, dtype=int)]).T
        BW_correct = np.linspace(0, int(sampling_speed/2) -1, int(fft_point/2)) *10**6 # MHz
        RF_correct = np.meshgrid(BW_correct, PP_correct.T)[0] + observing_frequency*10**6  # MHz
        visibility *= np.exp(-2*np.pi*1j*delay/(sampling_speed*10**6)*BW_correct) * np.exp(-2*np.pi*1j*rate*(PP_correct*effective_integration_length)) #* (1/2 * np.exp(-2*np.pi*1j*acel_correct*(PP_correct*effective_integration_length)**2))

    freq_rate_2D_array = np.fft.fftshift(scipy.fft.fft(visibility, axis=0, n=integ_fft), axes=0) * fft_point / length

    return freq_rate_2D_array

def frinZsearch(frinZspectrum, **kwargs) :

    lag_rate_2D_array  = np.fft.ifftshift(scipy.fft.ifft(freq_rate_2D_array, axis=1, n=fft_point, workers=cpu), axes=1)
    lag_rate_2D_array  = lag_rate_2D_array[:, ::-1]        # 列反転，これは delay が０を中心に対称になるため．


    return lag_rate_2D_array
"""
