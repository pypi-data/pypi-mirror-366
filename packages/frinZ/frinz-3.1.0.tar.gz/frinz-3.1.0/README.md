# 概要
frinZ.py のモジュール化．   
- https://github.com/M-AKIMOTOO/frinZ.py

# インストール
``` pip install frinZ ```  or  ``` pip3 install frinZ ```

# PyPI  
- https://pypi.org/project/frinZ/3.0.0/

# LICENSE 
MIT License (https://mit-license.org/)

# Google Colab
- https://colab.research.google.com/drive/1_mFX_tYkQfjvtVWDHvsQvNsbrqdSFrz8?hl=ja#scrollTo=JOHmPddbGOwP

# 例
章立てに例を示しているが，それぞれに共通する変数（例えば章１と章２の header や visibitily）は同じものを指す．
## １．cor ファイルのヘッダーとビジビリティを取得する
データ（cor ファイル）： https://github.com/M-AKIMOTOO/frinZ.py/tree/main/data 
``` python
import frinZ 

ifile = "YAMAGU34_HITACH32_2023262102100_all.cor"

header = frinZ.cor.header(ifile)
# type(header) = dict
# header.keys() show keys of header

visibility = frinZ.cor.visibility(ifile, skip=0, header=header)
# len(visibility) = 3
# visibility[0] = Complex spectrum 
# visibility[1] = Oserving time since 1970-01-01 00:00:00 UTC
# visibility[2] = effective_integration_length, which is output in xml-file 
# ここで遅延補正（sample 単位の delay と Hz 単位の rate）もできる．例えば visibility = frinZ.cor.visibility(ifile, delay=11.1, rate=0.123, skip=0, header=header)
```

## ２．クロスパワースペクトル
``` python
# クロスパワースペクトル

spectrum = frinZ.cor.frinZspectrum(
                                    visibility,
                                    length=header["PP"], 
                                    loop=0, 
                                    header=header)

# 観測時間方向，つまり変数 visibility[0] の縦方向で FFT を実行する．周波数シフトは行われている．
# RFI を除去することもできる．ただしダブルクォートで囲む必要あり．複数選択可能で，10--100 MHz だけなら rfi=["10,100"] とすればいいし，400--512 MHZ も合わせて除去したいなら rfi=["10,100","400,512"] とする．
# 変数 spectrum は要素 2，つまり len(spectrum) = 2 で，spectrum[0] = 積分する開始時刻，spectrum[1] = FFT した結果．
#
# length を変更すれば短時間積分が可能であるし，for 文で loop を回すこともできる．ただし，frinZspectrum では length と loop の値から loop 回数を制御することはしていない．つまり観測時間が 600 秒で length = 60，loop = 100 としたときに，loop < 10 で停止しないので，これを自分で制御する必要がある．この方法は単純に変数 header から観測時間に相当する PP を変数へ格納して，自分で設定した length で割って loop とすればいい．つまり loop = PP/length とすれば良い．
length = 10
pp = header["PP"] # e.g. 120
loop_cal = int(pp/length) # = 12 
for loop in range(loop_cal) :
    spectrum = frinZ.cor.frinZspectrum(
                                       visibility,
                                       length=length, 
                                       loop=loop, 
                                       header=header
                                       )
# とする．もちろん短時間積分でクロスパワースペクトルやフリンジを計算するなら，以降の章で説明する例は for 文の中に書かなければならない．
```

## 3. フリンジ
``` python
# フリンジ
search = frinZ.cor.frinZsearch(spectrum, fft_point=header["FFT"])
# 引数は frinZ.cor.frinZspectrum で出力されるスペクトルデータとヘッダーから FFT 点数だけ．
# 周波数シフトは行われている．
``` 

## 4. クロスパワースペクトルとフリンジのパラメーター推定
``` python
# 変数 spectrum と search のパラメータ推定のための準備
# 相関処理の設定から得られる周波数分解能や FFT した結果で得られる rate と delay のデータ.
# 変数 frequency，rate，delay は frinZparam の中で計算はされているので，ここでは使用することはない．frinZplot で利用する．
# bw は観測帯域幅．
frequency = frinZ.cor.frequency(fft_point=header["FFT"], 
                                bw=int(header["Sampling-frequency-MHz"]/2))
rate = frinZ.cor.rate(frinZ.cor.zerofill(header["PP"]), 
                      effective_integration_length=visibility[2])
delay = frinZ.cor.delay(fft_point=header["FFT"])

param = frinZ.cor.frinZparam(lag_rate_2D_array=search, 
                       delay_win=[-10,30],
                       rate_win=[-0.1, 0.1], 
                       header=header,
                       length=header["PP"],
                       efective_integration_length=visibility[2])

# クロスパワースペクトルにおけるパラメーター推定には引数 freq_rate_2D_array を指定して，フリンジのパラメータ推定には lag_rate_2D_array を指定する．つまり，上記の例ではフリンジのパラメータ推定を行っている．それらを同時に指定することはできない．
# type(param) = dict．param.keys() で dict の key を確認できる．
# クロスパワースペクトルの場合の param の key は"phase_list"，"spectrum_list"，"rate_list"， "fringe_amp"， "fringe_phase"，"fringe_spectrum"，"snr"，"noise"．フリンジの場合は "delay_list"，"rate_list"，"fringe_amp"，"fringe_phase"，"res_delay"，"res_rate"，"snr"，"noise"．
# delay_win（単位は sample）と rate_win（単位は Hz）は同時に使用する必要があり，それらを用いることで任意の範囲でフリンジのパラメーターを推定することができる．
```

## 4. グラフでクロスパワースペクトルとフリンジを確認する
``` python
# 変数 visibility，spectrum，search の振幅と位相をプロットすることができる．
# type="vis" が変数 visibility の場合，type="freq" が変数 spectrum の場合，type="time" が変数 search の場合である． そして flag="amp" 振幅，flag="phase" で位相のグラフを表示する．よって 6 種類のグラフを確認できる．
# show はデフォルトでは False．
# 下記の場合はビジビリティの位相がグラフとして表示される．よって VLBI で位相遅延が不正確なら位相回転を確認することができる．実際に ifile は山口ー日立基線の観測データで，遅延補正が不正確なので，位相回転を確認できる．
frinZ.cor.frinZplot(frequency, rate, visibility[0], show=True, type="vis", flag="phase")
```


# frinZ で利用できる関数とその引数

- Radian2RaDec
    - ra_radian: float  
    - dec_radian: float  
     -> float  
    - return Ra_deg, Dec_deg
- RaDec2AltAz
    - object_ra_deg: float    
    - object_dec_deg: float  
    - observation_time_datetime: float  
    - latitude: float  
    - longitude: float  
    - height: float  
     -> float 
    - return object_altaz.az.deg, object_altaz.alt.deg, location_lon_lat.height.value
- header
    - ifile: str -> dict 
    - return header_region_info
- visibility
    - ifile: str
    -    delay: float = 0.0  
    -    rate: float = 0.0   
    -    acel: float = 0.0  
    -    skip: int = 0   
    -    header: Optional[dict] = None  
         -> Tuple[np.ndarray, List[int], float]  
    - return complex_visibility, obs_scan_time, effective_integration_length
- delay  
    - fft_point: int   
    - return delay
- rate  
    - fft_point, effective_integration_length
    - return rate
- frequency
    - fft_point, bw
    - return frequency
- label
    - ifile
    - return label
- epoch
    - obs_scan_time: datetime
    - return epoch0, epoch1, epoch2, epoch3, mjd 
- noise
    - input_2D_data: float
    - search_00_amp: float,
    - flag: str    
     -> float
    - return SNR, noise_level
- RFI 
    - r0
    - bw: int  
    - fft: int      
     -> int
    - return rfi_cut_min, rfi_cut_max, len(r0)
- frinZspectrum
    - visibility: Optional[List]
    - length: int
    - loop: int
    - rfi: Optional[List] = None,
    - header: Optional[dict] = None    
    -> Tuple[List, np.ndarray]:
    - return  observing_time, freq_rate_2D_array
- frinZsearch
    - spectrum: Optional[List]
    - fft_point: int   
        -> np.ndarray 
    - return lag_rate_2D_array
- frinZparam
    - freq_rate_2D_array: Optional[np.ndarray] = None
    - lag_rate_2D_array: Optional[np.ndarray] = None
    - delay_win: Optional[List] = None
    - rate_win: Optional[List] = None
    - effective_integration_length: float = 1.0 
    - header: Optional[dict] = None
    - return 
- frinZplot
    - xdata: Optional[np.ndarray] = None 
    - ydata: Optional[np.ndarray] = None 
    - zdata: Optional[np.ndarray] = None
    - type: str = ""
    - flag: str = ""
    - show: bool = False

