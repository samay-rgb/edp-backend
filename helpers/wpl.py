pl = 4.0  # reference path loss coefficient,
alpha = 2.0  # path loss exponent


def distance(rssi: list, alpha):
    '''This method will calculate the distance of each access point from the device using the RSSI values'''
    d = []
    for val in rssi:
        x = 10**((pl-val)/(10*alpha))
        # if val == 100.0:
        # x = 0
        d.append(x)
    return d


def calcWeight(dist):
    '''This method will calculate the weight of each access point from the device using the distance values'''
    w = []
    tot = 0
    for x in dist:
        if x != 0:
            tot = tot+1/x
        # tot=tot+1/x
    for val in dist:
        if val != 0:
            x = 1/(val*tot)
        else:
            x = 0
        w.append(x)
    return w


def calcLocation(weights, wifiLocs):
    '''This method will calculate the location of the device using the weights and the location of the access points'''
    x = 0
    y = 0
    for weight in weights:
        # print(wifiLocs['MAC'+str(weights.index(weight)+1)])
        xi = wifiLocs['MAC'+str(weights.index(weight)+1)][0]
        yi = wifiLocs['MAC'+str(weights.index(weight)+1)][1]
        x = x+xi*weight
        y = y+yi*weight
    return x, y


def getLocation(rssi, wifiLocs):
    '''This method will calculate the location of the device using the RSSI values and the location of the access points'''
    dist = distance(rssi, alpha)
    weights = calcWeight(dist)
    x, y = calcLocation(weights, wifiLocs)
    return x, y
