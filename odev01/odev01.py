import sys

sorusay = int(sys.argv[1])
sozluk = {}
count = 0
while (count < sorusay):
    count = count + 1
    control = 0
    print('Sirayla numara, isim, soyisim, yas girin:')
    y = input()
    x = y.split()
    if x[0].isdigit(): #numara sayi mi?
        numara = x[0]
        if numara in sozluk: #numara sozlukte var mi?
            print("Girilen numara sozlukte var, geçiliyor.")
        elif x[1].isdigit() or x[2].isdigit(): #numarada sorun yok, isim/ikinci isim kismina sayi girilmis mi?
            print("Hatali deger. Numara icin sayi, isim ve soyisim icin karakter, yas için sayi girin.")
        elif x[3].isdigit(): #isim/ikinci isimde sorun yok, girilen sonraki arguman soyad mi yoksa sayi (yas) mi? yas ise 2. isim yok onu soyad yap
            isim = x[1]
            soyisim = x[2]
            yas = x[3]
            control = 1
        elif x[4].isdigit(): #girilen sonraki arguman sayi degil o zaman soyadmis yani 2 isim var, sonraki arguman sayi mi?
            isim = x[1] + ' ' + x[2]
            soyisim = x[3]
            yas = x[4]
            control = 1
        else: #herhangi bir senaryo uymadi
            print("Hatali deger. Numara icin sayi, isim ve soyisim icin karakter, yas icin sayi girin.")
    else: #numara sayi degil
        print("Hatali deger. Numara icin sayi, isim ve soyisim icin karakter, yas icin sayi girin.")
    if control == 1: #her arguman formata uygun ve numara sozlukte degil, tuple olustur ve sozluge ekle
        tuple = (isim, soyisim, yas)
        sozluk[numara] = tuple
        control = 0
print("Sozluk sirali basiliyor:")
for key, value in sorted(sozluk.items(), key=lambda x: int(x[0])): #lambda fonksiyonu ile keyleri sort edip bas
    print("{} : {}".format(key, value))
