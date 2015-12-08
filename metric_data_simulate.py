import math

# if 'SINR', then sevral parameters--> neibor level,
def metric_management(metrics_command, argvList, rssi_packet, index_symbol):
    if metrics_command == 'SINR':
        return SINR_symbol_metric(rssi_packet, index_symbol, argvList[0])
    elif metrics_command == 'RSSI':
        return RSSI_symbol_metrics(rssi_packet, index_symbol, argvList[0])


    pass

# trans form the rssi raw data to dbm rssi data
def RSSI_raw2dbm(rssi_rawdata):
    return int(rssi_rawdata)  - 256 - 45

def calc_noise():
    emp_noise_dbm = -104
    return (dbm_to_mw(emp_noise_dbm))

def dbm_to_mw(dbm_data):
    return 10**((dbm_data-30) * 1.0/10)

def mw_to_dbm(mw_data):
    return 10 * math.log(mw_data * 1000, 10)
    # return 10 * math.log(abs(mw_data) * 1000, 10)

# the input rssi must be integer
def SINR_symbol_metric( rssi_packet, index_symbol, neighbor_level):
    noise_mw = calc_noise()
    minm_packet_RSSI_dbm = RSSI_raw2dbm(int(min(rssi_packet)))
    # majority_packet_RSSI_dbm = RSSI_raw2dbm(int(max(rssi_packet, key=rssi_packet.count)))
    signal_packet_mw = dbm_to_mw(minm_packet_RSSI_dbm) - noise_mw

    # calculate the extract fraction rssi data
    symbol_SINR = []
    [index_beg, index_end, symbol_SINR, start_poi] = filldata_for_learning(rssi_packet, index_symbol, neighbor_level, symbol_SINR)


    # calculate the corresponding training data of SINR for current symbol
    for i in range(index_beg, index_end):
        # if int(rssi_packet[i]) < 200:# skip the data that rssi is too small
        #     continue
        isymbolrssi_dbm = RSSI_raw2dbm(rssi_packet[i])
        isymbolrssi_mw = dbm_to_mw(isymbolrssi_dbm)
        # isymbolInterference_mw = dbm_to_mw(isymbolrssi_mw) - signal_packet_mw - noise_mw
        isymbolInterference_mw = isymbolrssi_mw - dbm_to_mw(minm_packet_RSSI_dbm)

        # symbol_SINR.append( signal_packet_mw/(isymbolInterference_mw + noise_mw) )
        # save the dbm value as the SINR, which is more accurate


        symbol_sinr_mwrate = signal_packet_mw/(isymbolInterference_mw + noise_mw)
        symbol_sinr_dbmrate = mw_to_dbm(symbol_sinr_mwrate)
        # symbol_sinr_dbmrate = mw_to_dbm(signal_packet_mw) - mw_to_dbm(isymbolInterference_mw + noise_mw)
        symbol_SINR.insert(start_poi, symbol_sinr_dbmrate)


        # print i, 'sinr[mw]%s,[dbm]%s,[sig_dbm]%s,%s,[inter+noist_dbm]%s,%s' % \
        #          (symbol_sinr_mwrate, symbol_sinr_dbmrate,
        #           signal_packet_mw, mw_to_dbm(signal_packet_mw),
        #           str(isymbolInterference_mw + noise_mw) , mw_to_dbm(isymbolInterference_mw + noise_mw))


        tmp_inter_dbm = ''
        tmp_sig_dbm = ''
        if isymbolInterference_mw <= 0:
            # print i,'sinr:%s, s:[mw]%s,[dbm]%s, i:[mw]%s,[dbm]%s, n:[mw]%s,[dbm]%s , rssi:%s,[mw]%s' % \
            #     (signal_packet_mw/(isymbolInterference_mw + noise_mw),
            #      signal_packet_mw,tmp_sig_dbm,
            #      isymbolInterference_mw, tmp_inter_dbm,
            #      noise_mw, mw_to_dbm(noise_mw),
            #      rssi_packet[i],isymbolrssi_mw)
            tmp_inter_dbm = '-1'
        else:
            tmp_inter_dbm = mw_to_dbm(isymbolInterference_mw)
        if signal_packet_mw <= 0:
            # print i,'sinr:%s, s:[mw]%s,[dbm]%s, i:[mw]%s,[dbm]%s, n:[mw]%s,[dbm]%s , rssi:%s,[mw]%s' % \
            #     (signal_packet_mw/(isymbolInterference_mw + noise_mw),
            #      signal_packet_mw,tmp_sig_dbm,
            #      isymbolInterference_mw, tmp_inter_dbm,
            #      noise_mw, mw_to_dbm(noise_mw),
            #      rssi_packet[i],isymbolrssi_mw)
            tmp_sig_dbm = '-1'
        else:
            tmp_sig_dbm =  mw_to_dbm(signal_packet_mw)
        if isymbolInterference_mw <0 or signal_packet_mw <=0:
            print i,'sinr:%s, s:[mw]%s,[dbm]%s, i:[mw]%s,[dbm]%s, n:[mw]%s,[dbm]%s , rssi:%s,[dmb]%s,[mw]%s, [minrssi]%s[dbm]%s' % \
                    (signal_packet_mw/(isymbolInterference_mw + noise_mw),
                     signal_packet_mw,tmp_sig_dbm,
                     isymbolInterference_mw, tmp_inter_dbm,
                     noise_mw, mw_to_dbm(noise_mw),
                     rssi_packet[i],isymbolrssi_dbm, isymbolrssi_mw,
                     min(rssi_packet), RSSI_raw2dbm(min(rssi_packet)))
    return symbol_SINR

def filldata_for_learning(packet_metrics, index_symbol, neighbor_level, metrics_list):
    start_poi = 0
    max_left_rssinum = neighbor_level
    max_right_rssinum = neighbor_level
    index_beg = index_symbol - max_left_rssinum
    if index_beg < 0:
        for i in range(abs(index_beg)):
            metrics_list.append(0)
        index_beg = 0
        start_poi = len(metrics_list)
    index_end = index_symbol + max_right_rssinum + 1
    if index_end > len(packet_metrics):
        for i in range(index_end - len(packet_metrics)):
            metrics_list.append(0)
        index_end = len(packet_metrics)
    return [index_beg, index_end, metrics_list, start_poi]

def calc_dif_RSSI(rssi_packet, rssi_selectfraction):
    # baseRSSI = int(max(rssi_packet,key=rssi_packet.count))
    baseRSSI = int(min(rssi_packet))

    for i in range(len(rssi_selectfraction)):
        rssi_selectfraction[i] = int(rssi_selectfraction[i]) - baseRSSI
    return rssi_selectfraction

# using multiple rssi value surrounded with data as input to training the model
# the rssi value still is the difference between the majority.
def RSSI_symbol_metrics(rssi_packet, index_data, neighbor_level):

    symbol_RSSI = []
    [index_beg, index_end, symbol_RSSI, start_poi] = filldata_for_learning(rssi_packet, index_data, neighbor_level, symbol_RSSI)
    rssi_fraction = calc_dif_RSSI(rssi_packet, rssi_packet[index_beg: index_end])
    for eachrssi in rssi_fraction:
        symbol_RSSI.insert(start_poi, eachrssi)

    return symbol_RSSI
    pass
