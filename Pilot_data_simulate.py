import rawDataExactor as rde
import random
import SSER_online_train as ot



# split each packet into symbol
def SplitEachPacket2Symbol(data, len_symbol):
    pass


#directly using the rssi data corresponding to the data
def one_one_RSSI_metrics(rssi_packet, index_data):
    return [rssi_packet[index_data]]
    pass

# using multiple rssi value surrounded with data as input to training the model
# the rssi value still is the difference between the majority.
def multi_one_RSSI_metrics(rssi_packet, index_data):
    max_left_rssinum = 2
    max_right_rssinum = 2
    index_beg = index_data - max_left_rssinum
    if index_beg < 0:
        index_beg = 0
    index_end = index_data + max_right_rssinum + 1
    if index_end > len(rssi_packet):
        index_end = len(rssi_packet)
    return rssi_packet[index_beg:index_end]
    pass

# generate the metrics that the training data input
# input the rssi trace, and return the metrics parameters list corresponding to the data trace
def generateTrainMetrics(rssi_packet, index_data):
    # return one_one_RSSI_metrics(rssi_packet, index_data)

    return multi_one_RSSI_metrics(rssi_packet, index_data)
    pass


# Pilot_data_alltrace : [ [for each packet],[ [chosed pilot data],[RSSI,snr]   ]  ]
# pilot_data_packet: [ [chosed pilot data],[RSSI,snr]   ]
# pilot_ser_alltrace : [ [for each packet],[ [chosed pilot ser],[ser] ] ]
def choosePilot(data,rssi, pilot_step):
    Pilot_data_alltrace = []
    pilot_ser_alltrace = []
    random.seed(3)
    for pkgindex in range(len(data)):
        pilot_data_packet = []
        pilot_ser_packet = []
        for plindex in range(0, len(data[pkgindex]), pilot_step):
            if data[pkgindex][plindex] != '0':# if current symbol is wrong ,
                pilot_ser_packet.append(random.uniform(0.99,1)) # assume the pilot error has high confidence
            else:
                pilot_ser_packet.append(random.uniform(0,0.01)) # assume the pilot error has low confidence
            pilot_data_element = generateTrainMetrics(rssi[pkgindex], plindex)
            pilot_data_packet.append(pilot_data_element)
        Pilot_data_alltrace.append(pilot_data_packet)
        pilot_ser_alltrace.append(pilot_ser_packet)
    # print 'pilot',len(pilot_ser_alltrace[1]),len(Pilot_data_alltrace[1])
    return [Pilot_data_alltrace, pilot_ser_alltrace]
    pass

def chooseOthersymbol(data,rssi, pilot_step):
    other_data_alltrace = []
    for i in range(len(data)):
        other_data_paket = []
        for j in range(len(data[i])):
            if j % pilot_step == 0:
                continue
            other_data_element = generateTrainMetrics(rssi[i],j)
            # print '[pick%d-%d][rssi]:%s\n' % (i,j,rssi[i][j]),
            other_data_paket.append(other_data_element)
        other_data_alltrace.append(other_data_paket)
    # print 'other symol',len(other_data_alltrace[1])
    return other_data_alltrace
    pass

# get the difference between baseRSSi and rssi
def calcdif_rssi( rssiTrace):
    difrssi_alltrace = []
    for i in range(len(rssiTrace)):
        baseRSSI = int(max(rssiTrace[i],key=rssiTrace[i].count))
        difrssi_packet = []
        for j in range(len(rssiTrace[i])):
            newrssi = int(rssiTrace[i][j])- baseRSSI
            difrssi_packet.append(newrssi)
        difrssi_alltrace.append(difrssi_packet)
    return difrssi_alltrace
    pass

# filter the protocol header and tailer data. using only the pakcet content data
def protocal_802_15_4_modify(s_dataTrace, s_rssiTrace, len_symbol):
    filter_head = 8/len_symbol * 12 # the number of filtered fraction after scaled
    filter_tail = 8/len_symbol * 2
    for i in range(len(s_dataTrace)):
        s_dataTrace[i] = s_dataTrace[i][:len(s_dataTrace[i]) - filter_tail]
        s_dataTrace[i] = s_dataTrace[i][filter_head:]
        s_rssiTrace[i] = s_rssiTrace[i][:len(s_rssiTrace[i]) - filter_tail]
        s_rssiTrace[i] = s_rssiTrace[i][filter_head:]
    return [s_dataTrace, s_rssiTrace]
    pass

def simulated_tracebase(isDiffRssi):
    len_symbol = 8
    pilot_step = 8  # every pilot_step to get samples, actually is pilot_step*len_symbol.
    packet_len = 110
    thres_dtlength = packet_len * (8/ len_symbol)

    [dataTrace, rssiTrace] = rde.readTrace("rx-0-22-11-20140629-15-47-41-with_interference_802.11g")

    # dataTrace = rde.simpleSplit(dataTrace)# split the data trace into symbol, 4 bit/symbol in this case
    [s_dataTrace, s_rssiTrace] = rde.scaledRSSI(dataTrace, rssiTrace, thres_dtlength)# linear insert value

    #filter head and tail
    [s_dataTrace, s_rssiTrace] = protocal_802_15_4_modify(s_dataTrace, s_rssiTrace,len_symbol)
    # comment here to print the gnuplot data
    if isDiffRssi:
        s_rssiTrace = calcdif_rssi(s_rssiTrace)
    return [s_dataTrace, s_rssiTrace, pilot_step]
    pass

def UnkonwSymbolPayload(isDiffRssi):
    [data, rssi, pilot_step] = simulated_tracebase(isDiffRssi)
    unkonwSymbolp = []
    for i in range(len(data)):
        unkonwSymbolp_paket = []
        for j in range(len(data[i])):
            if j % pilot_step == 0:
                continue
            # unkonwSymbolp_element.append(data[i][j])
            unkonwSymbolp_paket.append(data[i][j])
        unkonwSymbolp.append(unkonwSymbolp_paket)
    # print 'palylaod',len(unkonwSymbolp[1])
    return unkonwSymbolp
    pass

def simulated_unkonw_symbol(isDiffRssi):
    [split_data, split_rssi, pilot_step] = simulated_tracebase(isDiffRssi)

    # print split_rssi[0]
    other_data_alltrace = chooseOthersymbol(split_data,split_rssi, pilot_step)
    # for i in range(len(other_data_alltrace[0])):
    #     print "[%d][rssi]:%s\n" % (i, other_data_alltrace[0][i][0])

    return other_data_alltrace
    pass


def simulated_pilot_generate(isDiffRssi):
    [split_data, split_rssi, pilot_step] = simulated_tracebase(isDiffRssi)
    [pilot_data_alltrace, pilot_ser_alltrace] = choosePilot(split_data, split_rssi, pilot_step)
    return [pilot_data_alltrace, pilot_ser_alltrace]
    pass


def relatedError(est_ser, gt_ser):
    RE = []
    for i in range(len(est_ser)):
        # diff = est_ser[i]  - gt_ser[i]

        RE.append("[%d]est-%s, gt-%s\n" % (i, str(est_ser[i]), str(gt_ser[i]) ))
    return RE
    pass

# estimate the ser
def naive_estimator(data, rssi, pilot_step):
    EST_SER_allpacket = []
    for pkgindex in range(len(rssi)):
        baseRSSI = int(max(rssi[pkgindex],key=rssi[pkgindex].count))
        temphigh = baseRSSI + 5
        templow = baseRSSI + 2

        #determine the low and high according to the pilot
        for plindex in range(0, len(rssi[pkgindex]), pilot_step):
            if data[pkgindex][plindex] != '0':# if current bit is wrong , then update the minim RSSI for high
                temphigh = min(temphigh, rssi[pkgindex][plindex])
            else:
                templow = max(templow, rssi[pkgindex][plindex])


        error_symbol_counter =0
        for rsindex in range(len(rssi[pkgindex])):
            if rssi[pkgindex][rsindex] >= temphigh:
                error_symbol_counter += 1
            elif rssi[pkgindex][rsindex] < temphigh and rssi[pkgindex][rsindex] > templow:
                count = (rssi[pkgindex][rsindex] - templow) * 1.0/ (temphigh - templow)
                error_symbol_counter += count
        est_pkg_ser = error_symbol_counter * 1.0 / len(rssi[pkgindex])
        if est_pkg_ser == 1:
            print templow, temphigh
            print rssi[pkgindex][:12]

        EST_SER_allpacket.append(est_pkg_ser)
    return EST_SER_allpacket
    pass

# default that data all zero, then the SER for every packet
def GroundTruth_SER_pktAverage(data):
    GT_SER_allPacket = []
    for eachPacket in data:
        error_symbol_counter = 0
        for eachsymbol in eachPacket:
            if eachsymbol != '0':
                error_symbol_counter += 1
        pkg_ser = error_symbol_counter * 1.0/ len(eachPacket)
        GT_SER_allPacket.append(pkg_ser)
    return GT_SER_allPacket
    pass


