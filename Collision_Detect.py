import numpy as np
import scipy as sp
import sqlite3
import math
import sklearn

db_address = 'D:\WIFI_BL\data.db'
sqlConn = sqlite3.connect(db_address)

def predict(input_array):
    N = len(input_array)
    threshold_check_match = 3
    Flag = False
    
    if(N%2==0):
        check_match = []
        A_matrix1 = np.array_split(input_array,2)
        while(Flag == False):
            for i in range(len(A_matrix1[0])):
                for j in range(len(A_matrix1[1])):
                    if(i==j):
                        R = A_matrix1[0][i]-A_matrix1[1][j]
                        check_match.append(R)
            if(max(check_match) > threshold_check_match):
                A_matrix1 = np.concatenate((A_matrix1[0], A_matrix1[1]))
                A_matrix1 = np.delete(A_matrix1,[len(A_matrix1)-1, len(A_matrix1)-2])
                A_matrix1 = np.array_split(A_matrix1,2)
                check_match = []
            elif(max(check_match)<=threshold_check_match):
                Flag = True

        leng_princ = len(A_matrix1[0])
        spare = N%leng_princ
        return input_array[leng_princ+spare], A_matrix1[0]

    elif (N%2 != 0):
        A_matrix = np.delete(input_array, N-1)  
        check_match_2 = []
        A_matrix2 = np.split(A_matrix,2)
        while(Flag == False):        
            for i in range(len(A_matrix2[0])):
                for j in range(len(A_matrix2[1])):
                    if(i==j):
                        R2 = A_matrix2[0][i]-A_matrix2[1][j]
                        check_match_2.append(R2)
            if(max(check_match_2)>threshold_check_match):
                A_matrix2 = np.concatenate((A_matrix2[0], A_matrix2[1]))
                A_matrix2 = np.delete(A_matrix2, [len(A_matrix2)-1, len(A_matrix2)-2])
                A_matrix2 = np.array_split(A_matrix2, 2)
                check_match_2 = []
            elif(max(check_match_2)<= threshold_check_match):
                Flag = True

        leng_princ2 = len(A_matrix2[0])
        spare2 = N%leng_princ2
        return input_array[leng_princ2+spare2], A_matrix2[0]

def get_next(input_value, qty_next):
    out_matrix = [input_value]
    i = 0
    while(i<qty_next):
        i=i+1
        input_value = input_value +1
        out_matrix.append(input_value)
    return out_matrix

def get_last(input_value, qty_next):
    if(input_value > qty_next):
        out_matrix = [input_value]
        i = 0
        while(i<qty_next):
            i=i+1
            input_value = input_value -1
            out_matrix.append(input_value)
        return out_matrix
    elif(input_value <= qty_next):
        return 0
def check_matrix_blue(matrix, value):
    arr_check = 0
    for i in matrix:
        if(i != value):
            arr_check = arr_check +1
    if(arr_check > 0):
        return False
    elif(arr_check == 0):
        return True

cursor = sqlConn.cursor()
strQuery = " select * from symbol where type = '11' "
cursor.execute(strQuery)
record = cursor.fetchall()

cursor.close()
interleav_matrix = []
for row in record:
    #print(row[7])
    id_wifi = row[7]
    parameter = [int(id_wifi)-1, int(id_wifi)+1]
    strQ_check_interleave = 'select symbol_ID,  type from symbol where symbol_ID = ? or symbol_ID = ?'
    cursor2 = sqlConn.cursor()
    cursor2.execute(strQ_check_interleave, parameter)
    record_2 = cursor2.fetchall()
    cursor2.close()
    blue_count = 0
    for row2 in record_2:
        if row2[1] == 10:
            blue_count = blue_count +1
    if blue_count == 2:
        interleav_matrix.append(parameter)
#print(interleav_matrix)

count_collision_matrix = []
for data in interleav_matrix:
    pulse_id_arr = get_last(data[0],7)[::-1]
    cursor = sqlConn.cursor()
    query_get_real_int = 'select dist_to_last_same_sym from symbol where symbol_ID = ?'
    cursor.execute(query_get_real_int, [int(data[1])])
    q_res = cursor.fetchall()
    cursor.close()
    real_bl_intv = q_res[0][0]
    bl_interval_arr = []
    bl_type_check_arr = []
    for el in pulse_id_arr:
        cursor = sqlConn.cursor()
        query_get_intv = 'select type, dist_to_last_same_sym from symbol where symbol_ID = ?'
        cursor.execute(query_get_intv, [int(el)])
        query_res = cursor.fetchall()
        cursor.close()
        bl_type_check_arr.append(int(query_res[0][0]))
        bl_interval_arr.append(int(query_res[0][1]))
    if(check_matrix_blue(bl_type_check_arr, 10) == True):
        predict_value = predict(bl_interval_arr)[0]
        if(real_bl_intv - predict_value > 5 or real_bl_intv - predict_value < - 5):
            collision_wifi_detected = data[1] -1
            count_collision_matrix.append(collision_wifi_detected)


print(count_collision_matrix)
print(len(count_collision_matrix))
    
#print(len(interleav_matrix))
#A = [1,2,2,3,4,4,1,2,2,3,4,4,1,2,2,3,4,4]
#B=[1008, 497, 496, 1009, 496, 496, 1009, 496]
#print(predict(bl_interval_arr))
#print(get_last(10,7)[::-1])