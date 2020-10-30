import numpy as np
import matplotlib.pyplot as plt

file = open('data\lab8_2.09-8.08-1.52.mbd', "r")
Lines = file.readlines()

data_dictionary = {}

for line in Lines: #okuma ve gecici sozluk olusturma
    line = line.rstrip("\n") #endofline ve virgul bol
    line = line.split(",")
    key = line[0]
    del line[0]
    data_dictionary[key] = line #key timestamp kalanlar value

pair_data = {} #anahtari alici verici cifti olacak verisi RSSI olacak sozluk
pair_timestamps = {} #anahtari alici verici cifti olacak verisi timestamp olacak sozluk

for key in data_dictionary: #gecici sozlukte timestampleri tara
    current = data_dictionary[key]
    tuple = (current[0], current[1]) #timestampteki alici verici ciftini al
    if tuple in pair_data: #cift zaten varsa veriyi cifte ekle
        pair_data[tuple] = pair_data[tuple] + "," + current[2]
        pair_timestamps[tuple] = pair_timestamps[tuple] + "," + key
    else: #cift zaten yoksa olustur
        pair_data[tuple] = current[2]
        pair_timestamps[tuple] = key



pair_minmax = {} #key cift, veri minmax
pair_zeros = {} #key cift, veri zero array
pair_step = {} #key cift, veri arange
for key in pair_data: #ciftleri tara
    numbers = pair_data[key].split(",") #ciftin verilerini al
    for i in range(0, len(numbers)): #ciftteki veri sayisi kadar don ve verileri int turune cevir
        numbers[i] = int(numbers[i])
    min = numbers[0]
    max = numbers[0]
    for n in numbers: #min max bulan dongu
        if n < min:
            min = n
        elif n > max:
            max = n

    minmax = [min, max]
    pair_minmax[key] = minmax
    pair_step[key] = np.arange(min, max+1)
    pair_zeros[key] = np.zeros(len(pair_step[key]))


for key in pair_data: #ciftleri tara
    zero_array = pair_zeros[key] #zero ve step arrayleri gecici degiskenlere ata
    step_array = pair_step[key]
    numbers = pair_data[key].split(",")
    for i in range(0, len(numbers)): #veri sayisi kadar don, int e cevir ve zero arrayde degerin sirasina karsilik gelen sayiyi arttir
        numbers[i] = int(numbers[i])
        index = np.where(step_array == numbers[i])
        zero_array[index] += 1
    pair_zeros[key] = zero_array #degisikligi kaydet

fig, axs = plt.subplots(2, 4, figsize = (20, 10))
fig.tight_layout()
x = 0
y = 0
for key in pair_data: #ciftleri tara
    axs[x, y].bar(pair_step[key],pair_zeros[key]) #axlar step ve arttirilmis zero array
    axs[x, y].set_title(key, fontsize = 10)
    if y == 3:
        y = 0
        x = 1
    else:
        y += 1
plt.show() #figuru bastir

fig, axs = plt.subplots(2, 4, figsize = (20, 10))
fig.tight_layout()
x = 0
y = 0
pair_frequencies = {}
for key in pair_data: #ciftleri tara
    i = 0
    numbers = pair_data[key].split(",")
    res = [float(idx) for idx in pair_timestamps[key].split(',')] #timestamp verilerini stringden float listesine cevir
    for n in range(0, len(numbers)): #veri sayisi kadar don
        if n == 99: #100 veri saydik, frekans hesabina basla
            freq = 100/(res[n]-res[n-99])
            pair_frequencies[key] = [freq]
        elif n > 99:
            freq = 100/(res[n]-res[n-99])
            pair_frequencies[key].append(freq)
    axs[x,y].plot(np.arange(0, n-98), pair_frequencies[key]) #axlar frekans degisimi sayisi ve frekanslar
    axs[x, y].set_title(key, fontsize = 10)
    if y == 3:
        y = 0
        x = 1
    else:
        y += 1

plt.show() #figuru bastir

fig, axs = plt.subplots(2, 4, figsize = (20, 10))
fig.tight_layout()
x = 0
y = 0

steps = np.arange(1.5, 2.5, 0.05) #1.5 - 2.5 arasi 0.5 adimla array olustur
zero_array = np.zeros(len(steps)) #1.5 - 2.5 arrayi uzunlugunda zero array olustur

for key in pair_data: #ciftleri tara
    i = 1.5
    n = 0
    zeros = zero_array #gecici degiskenler
    freqs = pair_frequencies[key]
    while i < 2.5: #stepleri tara
        for freq in freqs: #frekanslari tara
            if freq > i and freq < (i + 0.05): #araliga uyan her frekans icin araliga denk gelen degeri zero arrayde 1 arttir
                zeros[n] += 1
        i+=0.05
        n+=1
    axs[x, y].bar(steps,zeros) #axlar step ve arttirilmis zero array
    axs[x, y].set_title(key, fontsize = 10)
    if y == 3:
        y = 0
        x = 1
    else:
        y += 1
plt.show() #figuru bastir