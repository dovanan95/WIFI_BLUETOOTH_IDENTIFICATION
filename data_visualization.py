import numpy as np
import scipy as sp
import sqlite3
import math
import sklearn
import matplotlib.pyplot as plt 
import Collision_Detect

db_address = 'D:\WIFI_BL\data.db'
sqlConn = sqlite3.connect(db_address)

cursor = sqlConn.cursor()
str_max_ID = 'select max(symbol_ID) from symbol'
cursor.execute(str_max_ID)
max_ID = cursor.fetchall()
cursor.close()
sym_max_ID = int(max_ID[0][0])

cursor_wifi = sqlConn.cursor()
query_wifi = "select symbol_ID from symbol where type ='11'"
cursor_wifi.execute(query_wifi)
wifi_res = cursor_wifi.fetchall()
cursor_wifi.close()

wifi_matrix = []
for i in wifi_res:
    wifi_matrix.append(int(i[0]))


cursor_blue = sqlConn.cursor()
query_blue = "select symbol_ID from symbol where type ='10'"
cursor_blue.execute(query_blue)
blue_res = cursor_blue.fetchall()
cursor_blue.close()

blue_matrix = []
for i in blue_res:
    blue_matrix.append(int(i[0]))


full_data = list(range(0,sym_max_ID))

collision_wifi = Collision_Detect.count_collision_matrix

interleaving_wifi = Collision_Detect.intl_matrix_wifi


def get_one_1D(A,B):
    if(len(A)>len(B)):
        Z=np.zeros(len(A))
        for i in range(len(B)):
            Z[B[i]-1]=1
        return Z
    elif(len(B)>len(A)):
        Z=np.zeros(len(B))
        for i in range(len(A)):
            Z[[A[i]-1]]=1
        return Z


Z_wifi = get_one_1D(full_data,wifi_matrix)
Z_blue = get_one_1D(full_data, blue_matrix)
Z_interleaving = get_one_1D(full_data, interleaving_wifi)
Z_collision = get_one_1D(full_data,collision_wifi)

plt.subplot(4,1,1)
plt.stem(Z_wifi)
plt.title('Wi-Fi position')
#plt.ylabel('Wi-Fi position')
plt.subplot(4,1,2)
plt.stem(Z_blue)
plt.title('Bluetooth position')
#plt.ylabel('Bluetooth position')
plt.subplot(4,1,3)
plt.stem(Z_interleaving)
plt.title('Interleaving position')
#plt.ylabel('Interleaving position')
plt.subplot(4,1,4)
plt.stem(Z_collision)
plt.title('Collision position')
#plt.ylabel('Collision position')


plt.show()



