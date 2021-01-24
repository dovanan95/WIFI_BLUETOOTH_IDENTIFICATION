"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
from numpy.core.fromnumeric import std
import pywt 
import pmt
import numpy
import pandas
import scipy
import math
import sklearn
from sklearn import preprocessing
import os
import csv
import pickle
import time
import sqlite3
#import keras
from scipy.stats import linregress
from datetime import datetime
from scipy import stats, optimize, interpolate
from gnuradio import digital

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, example_param=1.0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Core',   # will show up in GRC
            in_sig=[np.complex64, np.float32], 
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.example_param = example_param
        self.db_address = 'D:\WIFI_BL\data.db'
        self.message_port_register_out(pmt.intern("Signal_out"))

    
    def data_record(self, data):
        kur, vari, stdard, skewnes, peak, rms, sft = self.statis_param_computing(data)
        data_record = [kur, vari, stdard, skewnes, peak, rms, sft, 1]

        with open('D:\UAV\UAV\data_bl.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerow(data_record)

    def signal_record(self, signal_input):
        
        with open('D:\UAV\UAV\SAMPLE.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerow(signal_input)
            '''
        with open('D:\UAV\UAV\SAMPLE.txt', 'w') as f:
            f.write(signal_input)
            #f.close()
            '''
    def max_detector(self, signal_in):
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        N = len(signal_in)
        max_matrix = []
        for i in range(N-1):
            if (signal_in[i]> signal_in[i+1] and signal_in[i] > signal_in[i-1]):
                max_matrix.append(i)
        for j in range(len(max_matrix)-1):
            if((max_matrix[j+1] - max_matrix[j]) > N//20 ):
                #print(cur_time,  ': bluetooth')
                return (' bluetooth')
            else:
                #print(cur_time,  ': wifi or other')
                return(' wifi or other')

    def corv_hann(self, freq_sig_in):
        N = len(freq_sig_in)
        blu_window = N//25
        blu_overlap = blu_window/2
        wf_window = blu_window/2
        wf_overlap = wf_window/4
        #wf_beta = 10
        hann_window_wf = np.hanning(wf_window)
        hann_window_bl = np.hanning(blu_window)
        cor_matrix_blu = []
        cor_matrix_wf = []
        if(wf_window == 0 or blu_window ==0):
            return 0,0,0,0
        else:
            for i in range(0, N-blu_window, blu_window - blu_overlap):
                x_bl = freq_sig_in[i:(i+blu_window)]
                y_bl = freq_sig_in[(i + blu_window - blu_overlap): (i +2 * blu_window - blu_overlap)]
                if(len(x_bl)== len(y_bl)):
                    corr_blu = np.corrcoef(x_bl,y_bl)
                    corr_blu0 = corr_blu[0,1]
                    cor_matrix_blu.append(corr_blu0)
            for j in range(0, N - wf_window, wf_window-wf_overlap):
                x_wf = freq_sig_in[j:(j+wf_window)]
                y_wf = freq_sig_in[(j + wf_window - wf_overlap): (j +2 * wf_window - wf_overlap)]
                if(len(x_wf)==len(y_wf)):
                    corr_wf = np.corrcoef(x_wf, y_wf)
                    corr_wf0 = corr_wf[0,1]
                    cor_matrix_wf.append(corr_wf0)
            
            max_bl_matrix = np.max(cor_matrix_blu)
            max_wf_matrix = np.max(cor_matrix_wf)
            thrs_conv_bl =0
            thrs_conv_wf =0
            corr_thrs =0.5
            for i in cor_matrix_wf:
                if(i>corr_thrs):
                    thrs_conv_wf = thrs_conv_wf +1
            for j in cor_matrix_blu:
                if(j>corr_thrs):
                    thrs_conv_bl = thrs_conv_bl +1
            return max_bl_matrix, thrs_conv_bl, max_wf_matrix, thrs_conv_wf
                
    def max_and_dist_computing(self, signal_in):
        N = len(signal_in)
        max_matrix = []
        max_dis = []
        slope = []
        if(N != 0):
            for i in range(N-1):
                if (signal_in[i]> signal_in[i+1] and signal_in[i] > signal_in[i-1]):
                    max_matrix.append(i)
                    a = [i, signal_in[i]]
                    b = [i+1, signal_in[i+1]]
                    sl = linregress(a,b)[0]
                    slope.append(sl)
            num_of_max = len(max_matrix)
            for j in range(len(max_matrix)-1):
                r = max_matrix[j+1] - max_matrix[j]
                max_dis.append(r)
        
            max_dist = np.max(np.array(max_dis))
            max_slope = np.max(np.array(slope))
        
            min_slope = np.min(np.array(slope))
        else:
            pass

        return num_of_max, max_dist, max_slope,  min_slope
    def db_connect_exec(self, start_point, end_point, type_symbol, length_signal, signal_ID, dtls, dtlss, sym_ID, dte, sym_len):
        sqlConnection = sqlite3.connect(self.db_address)
        cursor = sqlConnection.cursor()

        parameter = [start_point, end_point, type_symbol, length_signal, signal_ID, dtls, dtlss, sym_ID, dte, sym_len]

        insert_querry = """insert into symbol(start_point, end_point, type, length_signal, signal_ID, dist_to_last_sym, dist_to_last_same_sym,
                            symbol_ID, dist_to_end, symbol_length) values (?,?,?,?,?,?,?,?,?,?)"""
        cursor.execute(insert_querry, parameter)
        sqlConnection.commit()
        cursor.close()

    def code_generator_signal(self):
        
        sqlConnection = sqlite3.connect(self.db_address)
        cursor = sqlConnection.cursor()
        querry = """select signal_ID from symbol order by signal_ID desc limit 1"""
        cursor.execute(querry)
        reccord = cursor.fetchone()
        if(reccord is None):
            return 1
        elif(len(reccord) > 0):               
            sig_id = reccord[0]
            new_Id = sig_id + 1
            return new_Id
        cursor.close()
     
    
    def code_generator_symbol(self):
        
        sqlConnection = sqlite3.connect(self.db_address)
        cursor = sqlConnection.cursor()
        querry = """select symbol_ID from symbol order by symbol_ID desc limit 1"""
        cursor.execute(querry)
        reccord = cursor.fetchone()
        if(reccord is None):
            return 1
        elif(len(reccord) > 0):
            sym_id = reccord[0]
            new_id = sym_id +1
            return new_id
        cursor.close()
        
    
    def dist_last_computing(self, start_point, signal_ID):
        sqlConnection = sqlite3.connect(self.db_address)
        cursor = sqlConnection.cursor()
        querry = """select end_point, type, length_signal, signal_ID, symbol_ID, dist_to_end 
                    from symbol order by symbol_ID desc limit 100"""
        cursor.execute(querry)
        record = cursor.fetchall()
        dist_to_last = 0
        for row in record:
            if(row[1] == 8):
                dist_to_last = dist_to_last + row[2]
            if(row[1] != 8):
                if(row[3] == signal_ID):
                    dist_to_last = start_point - row[0]
                elif(row[3] != signal_ID):
                    dist_to_last = dist_to_last + row[5] + start_point
                break   
        return dist_to_last
        cursor.close()

   def dist_last_same_computing(self, start_point, signal_ID, type_signal):
        sqlConnection = sqlite3.connect(self.db_address)
        cursor = sqlConnection.cursor()
        querry = """select end_point, type, length_signal, signal_ID, symbol_ID, dist_to_end 
                    from symbol order by symbol_ID desc limit 100"""
        cursor.execute(querry)
        record = cursor.fetchall()
        dist_to_last_same = 0
        signal_ID_check = []
        signal_length_matrix = []

        for row in record:
            if(type_signal == row[1]):
                if(signal_ID == row[3]):
                    dist_to_last_same = start_point - row[0]
                elif(signal_ID != row[3]):
                    if(len(signal_ID_check)>0):
                        for i in range(len(signal_ID_check)-1):
                            if(signal_ID_check[i]== signal_ID_check[i+1]):
                                signal_length_matrix[i+1] = 0
                        if(signal_ID_check[len(signal_ID_check)-1] == row[3]):
                            dist_to_last_same = start_point + sum(signal_length_matrix) + row[5] - row[2]
                        elif(signal_ID_check[len(signal_ID_check)-1] != row[3]):
                            dist_to_last_same = start_point + sum(signal_length_matrix) + row[5]
                        
                    elif(len(signal_ID_check) == 0):
                        dist_to_last_same = start_point + row[5]
                break
            elif(type_signal != row[1]):
                if(signal_ID == row[3]):
                    pass
                elif(signal_ID != row[3]):
                    signal_ID_check.append(row[3])
                    signal_length_matrix.append(row[2])

        return dist_to_last_same
        cursor.close()
        
    def symbol_computing(self, series_in):
        N = len(series_in)
        thrs_enrgy = 0.3
        neg_thrs_enrgy = -thrs_enrgy
        flag = 0
        counter = 0
        symbol = []
        for i in range(N-1):
            if((series_in[i]>thrs_enrgy and series_in[i]>=series_in[i-1] and series_in[i]>=series_in[i+1])
             or (series_in[i]< neg_thrs_enrgy and series_in[i]<=series_in[i-1] and series_in[i]<=series_in[i+1])):
                counter = counter + 1
                symbol.append(i)

        length_matrix = []
        for j in range(len(symbol)-1):
            dist = symbol[j+1] - symbol[j]
            #length_matrix.append(dist)
            if(dist > 10):
                length_matrix.append(j+1)
        
        symbol_ident = np.array_split(symbol, length_matrix)
        sig_ID = self.code_generator_signal()
        result = []       
        for n in symbol_ident:
            if(len(n)>0):  
                st_point = n[0]
                end_point = n[len(n)-1]
                leng_signal = N        
                sym_len = n[len(n)-1]-n[0]       
                if(n[len(n)-1]-n[0] < 18 and n[len(n)-1]-n[0] >=10):
                    type_signal = 10 #BLUETOOTH
                    dist_to_end = N - n[len(n)-1]
                    sym_ID = self.code_generator_symbol()
                    dtls = self.dist_last_computing(n[0], sig_ID)
                    dtlss = self.dist_last_same_computing(n[0], sig_ID, type_signal)       
                    self.db_connect_exec(n[0], n[len(n)-1], type_signal, leng_signal, sig_ID, dtls, dtlss, sym_ID, dist_to_end, sym_len)
                    result.append(['---------BLUETOOTH--------', n[0], n[len(n)-1]])
                elif(n[len(n)-1]-n[0] >= 75 and n[len(n)-1]-n[0] <= 100):
                    type_signal = 11 #WIFI
                    dist_to_end = N - n[len(n)-1]
                    sym_ID = self.code_generator_symbol()
                    dtls = self.dist_last_computing(n[0], sig_ID)
                    dtlss = self.dist_last_same_computing(n[0], sig_ID, type_signal)
                    self.db_connect_exec(n[0], n[len(n)-1], type_signal, leng_signal, sig_ID, dtls, dtlss, sym_ID, dist_to_end, sym_len)
                    result.append(['===========WIFI===========', n[0], n[len(n)-1]])
                else:
                    type_signal = 9 #UNKNOWN
                    dist_to_end = N - n[len(n)-1]
                    sym_ID = self.code_generator_symbol()
                    dtls = self.dist_last_computing(n[0], sig_ID)
                    dtlss = self.dist_last_same_computing(n[0], sig_ID, type_signal)
                    self.db_connect_exec(n[0], n[len(n)-1], type_signal, leng_signal, sig_ID, dtls, dtlss, sym_ID, dist_to_end, sym_len)
                    result.append('UNKNOWN')
            else:
                type_signal = 8 #NONE
                dist_to_end = N
                sym_ID = self.code_generator_symbol()
                st_point =0
                end_point=0
                dtls = 0
                dtlss =0
                result.append('NONE')
                self.db_connect_exec(0, 0, type_signal, N, sig_ID, dtls, dtlss, sym_ID, dist_to_end, 0)

        return  result

    def work(self, input_items, output_items):
        in0 = input_items[0]
        in1 = input_items[1]
        out0 = output_items[0]
        #coeffs = pywt.wavedec(in0, 'db1', level=2, mode='periodic')
        #coeffs_2 = pywt.wavedec(in1, 'db1', level=5, mode='periodic')
        """example: multiply with constant"""
        #output_items[0][:] = input_items[0] * self.example_param
        
        #get current time
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")

        print(cur_time, self.symbol_computing(in0))
        print(cur_time, len(in0))
      
        '''
        par_comp = coeffs_2[0]
        with open('D:\\UAV\\UAV\\data.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerow(par_comp)
        with open('D:\\UAV\\UAV\\data_label.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerow(label)'''
   
        return len(output_items[0])
