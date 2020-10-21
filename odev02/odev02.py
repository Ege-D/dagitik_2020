import sys

file = open('airlines.txt', "r")
Lines = file.readlines()
airlinesNetwork = {}
airlinesVisited = {}
airlinesPath = ""
check = 0

def isPartner(company, partner, airlinesNetwork):
    for current in airlinesNetwork[company]:
        if current == partner:
            return True
    return False

for line in Lines:
    line = line.rstrip("\n")
    line = line.split(",")
    key = line[0]
    del line[0]
    airlinesNetwork[key] = line


def canRedeem(company, goal, airlinesPath, airlinesVisited, airlinesNetwork):
    if company == goal:
        airlinesPath = airlinesPath + company
        print("Path to redeem miles: " + airlinesPath)
        return True
    elif company in airlinesVisited:
        return False
    elif isPartner(company, goal, airlinesNetwork):
        airlinesPath = airlinesPath + company + "->" + goal
        print("Path to redeem miles: " + airlinesPath)
        return True
    else:
        airlinesVisited[company] = "checked"
        newPath = company + "->"
        airlinesPath = airlinesPath + newPath
        for index in airlinesNetwork:
            if company == index:
                check = 1
                break
        if check == 0:
            return False
        foundPath = False
        index = 0
        while not foundPath:
            partners = airlinesNetwork[company]
            foundPath = canRedeem(partners[index], goal, airlinesPath, airlinesVisited, airlinesNetwork)
            index = index + 1
            if index == len(airlinesNetwork[company]):
                break

        if not foundPath:
            airlinesPath.replace(newPath, '')
        return foundPath

if not canRedeem(sys.argv[1], sys.argv[2], airlinesPath, airlinesVisited, airlinesNetwork):
    print("Can't convert miles between these companies.")