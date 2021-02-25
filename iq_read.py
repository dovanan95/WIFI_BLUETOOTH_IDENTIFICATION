from scipy.io import wavfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

samplerate, data = wavfile.read('D:\\WIFI_BL\\IQ_WB.wav')
#plt.figure()
data_load = data[15002300:15026000]
dt_load = []
for x in data_load:
    dt_load.append(x)

#plt.plot(data_load)
#plt.show()

def dbfft(x, fs, win=None, ref=32768):
    """
    Calculate spectrum in dB scale
    Args:
        x: input signal
        fs: sampling frequency
        win: vector containing window samples (same length as x).
             If not provided, then rectangular window is used by default.
        ref: reference value used for dBFS scale. 32768 for int16 and 1 for float
    Returns:
        freq: frequency vector
        s_db: spectrum in dB scale
    """
    N = len(x)  # Length of input sequence
    if win is None:
        win = np.ones(1, N)
    if len(x) != len(win):
            raise ValueError('Signal and window must be of the same length')
    x = x * win
    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(x)
    freq = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)

    # Convert to dBFS
    s_dbfs = 20 * np.log10(s_mag/ref)
    
    if len(freq) > len(s_dbfs):
        freq = freq[:len(s_dbfs)]
    if len(s_dbfs) > len(freq):
        s_dbfs = s_dbfs[:len(freq)]
        
    return freq, s_dbfs
    
#max_value = max(max(x) for x in data)
#min_value = min(min(x) for x in data)
max_value = 32500
min_value = -32800

def rescale(input_data, max_data, min_data):
    '''rescale data to range from -1 to 1'''
    max_scale = 1
    min_scale = -1
    total_dist = max_data - min_data
    scale_dist = max_scale - min_scale
    a = max_data - input_data
    b = input_data - min_data
    aa = float((scale_dist*a))/total_dist
    scaled_value = max_scale - aa
    return scaled_value

def data_stepping(x, step):
    data_out = []
    for i in range(len(x)):
        if(i%step == 0):
            data_out.append(x[i])
    return data_out


data_out = []
for i in range(len(dt_load)):
    dt_1 = rescale(dt_load[i][0], max_value, min_value)
    dt_2 = rescale(dt_load[i][1], max_value, min_value)
    dtt = [dt_1, dt_2]
    data_out.append(dtt)
step = 2
data_out_2 = data_stepping(data_out, step)

time = list(range(0,len(data_out)))
time = data_stepping(time, step)
time = np.transpose(time)
time = np.expand_dims(time, axis=1)
data_out_2 = np.hstack((data_out_2,time))

plt.figure()
plt.plot(data_out_2)
#plt.show()
print(data_out_2[-1564])

np.savetxt("D:\\WIFI_BL\\series_scaled_25_2.csv", data_out_2, delimiter=",")
#print(data_load[19383])
