import os,sys


# path_trace is the path of the packet trace
# return has two list. data trace and rssi trace.
def readTrace(path_trace):
    fp = open(path_trace, 'r')
    lines = fp.readlines()
    fp.close()
    stage = 0; strLine = ''
    dataTrace = []; rssiTrace = []
    for line in lines:
        if stage == 2:
            # current packet trace is insufficient
            if line.find('|') == -1:
                # print 'data is insufficient'
                stage = 0
                continue
            data = line.replace(' | ', ' ').replace('  ', ' ').replace('\n', '').replace('\n', '')[ : -1].split(' ')
            rssiTmp = strLine.replace('  ', ' ').replace('\n', '').replace('\n', '')[ : -1].split(' ')
            rssi = []
            # filter the rssi of preamable bits
            for i in range(len(rssiTmp)):
                if rssiTmp[i] != '0':
                    rssi.append(rssiTmp[i])
            stage = 0
            dataTrace.append(data)
            rssiTrace.append(rssi[1:])
        if line.find('rssi_array') != -1:
            stage = 1
            strLine = line
        if stage == 1 and line.find('received') != -1:
            stage = 2

    # [dataTrace, rssiTrace] = scaledRSSI(dataTrace, rssiTrace)

    return [dataTrace, rssiTrace]

# simple split for 4 symbol length, the rssi are split correspondingly
def simpleSplit(data):
    split_data = []
    for eachPacket in data:
        packet = []
        tempdata = [] # used to save the procedure of each data
        for eachData in eachPacket:
            tempdata = list(eachData)
            if len(tempdata) < 2:
                tempdata.insert(0, '0')
            packet.extend(tempdata)
        split_data.append(packet)
    return split_data
    pass


def scaledRSSI(dataTrace, rssiTrace, thres_dtlength):
    scaled_rssi_Trace = []
    filtered_data_Trace = [] # insufficient data trace is filtered
    for i in range(len(dataTrace)):
        len_dt = len(dataTrace[i])
        len_rt = len(rssiTrace[i])
        if len_dt < thres_dtlength or len_rt <= 0:
            continue
        scaled_rssi = []
        for j in range(len_dt):
            insert_point = j * len_rt / len_dt
            left = int(insert_point)
            right = left + 1
            if right == len_rt:# index overflow
                right = left
            dif_fraction = insert_point - left
            try:
                dif_RSSI = int(rssiTrace[i][right], 10) - int(rssiTrace[i][left], 10)
            except:
                print right, len_dt, len_rt, left
            scaled_rssi.append( str(int(  int(rssiTrace[i][left]) + (dif_fraction * dif_RSSI))) )

        scaled_rssi_Trace.append(scaled_rssi)
        filtered_data_Trace.append(dataTrace[i])
    return [ filtered_data_Trace, scaled_rssi_Trace]
    pass


# [dataTrace, rssiTrace] = readTrace("rx-0-22-11-20140629-15-47-41-with_interference_802.11g")
# print len(rssiTrace)
# for eachrssi in rssiTrace:
#     # print eachrssi
#     print len(eachrssi)