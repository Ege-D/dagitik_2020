import sys

file = open('airlines.txt', "r")
Lines = file.readlines()
airlinesNetwork = {}
airlinesVisited = {}
airlinesPath = ""
check = 0

def isPartner(company, partner, airlinesNetwork): #verilen company icin verilen partnerin olup olmadigini donduren fonksiyon
    for current in airlinesNetwork[company]:
        if current == partner:
            return True
    return False

for line in Lines: #yukarida satirlara boldugum listeden end of line karakterlerini ve virgulleri atip sozluklere yerlestiren dongu
    line = line.rstrip("\n")
    line = line.split(",")
    key = line[0]
    del line[0]
    airlinesNetwork[key] = line


def canRedeem(company, goal, airlinesPath, airlinesVisited, airlinesNetwork):
    if company == goal: #kontrol edilen sirket aradigimiz sirket mi?
        airlinesPath = airlinesPath + company
        print("Path to redeem miles: " + airlinesPath)
        return True
    elif company in airlinesVisited: #degil, bu sirkete daha once geldik mi?
        return False
    elif isPartner(company, goal, airlinesNetwork): #gelmedik, bu sirketin partnerleri arasinda aradigimiz sirket var mi?
        airlinesPath = airlinesPath + company + "->" + goal
        print("Path to redeem miles: " + airlinesPath)
        return True
    else: #yok, sirketi yola ekle, gelinen sirketler listesine ekle
        airlinesVisited[company] = "checked"
        newPath = company + "->"
        airlinesPath = airlinesPath + newPath
        for index in airlinesNetwork: #sirket networkte var mi?
            if company == index:
                check = 1
                break
        if check == 0:
            return False
        foundPath = False
        index = 0
        while not foundPath: #partnerlerden aramaya devam et
            partners = airlinesNetwork[company]
            foundPath = canRedeem(partners[index], goal, airlinesPath, airlinesVisited, airlinesNetwork)
            index = index + 1
            if index == len(airlinesNetwork[company]):
                break

        if not foundPath: #cikmaza ciktik, geri don ve bu sirketi yoldan cikar
            airlinesPath.replace(newPath, '')
        return foundPath

if not canRedeem(sys.argv[1], sys.argv[2], airlinesPath, airlinesVisited, airlinesNetwork):
    print("Can't convert/redeem miles between these companies.")