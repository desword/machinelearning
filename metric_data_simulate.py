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
    emp_noise_dbm = -93
    return (dbm_to_mw(emp_noise_dbm))

def dbm_to_mw(dbm_data):
    return 10**((dbm_data-30) * 1.0/10)

def mw_to_dbm(mw_data):
    return 10 * math.log(abs(mw_data) * 1000, 10)

# the input rssi must be integer
def SINR_symbol_metric( rssi_packet, index_symbol, neighbor_level):
    noise_mw = calc_noise()
    majority_packet_RSSI_dbm = RSSI_raw2dbm(int(min(rssi_packet)))
    # majority_packet_RSSI_dbm = RSSI_raw2dbm(int(max(rssi_packet, key=rssi_packet.count)))
    signal_packet_mw = dbm_to_mw(majority_packet_RSSI_dbm) - noise_mw

    # calculate the extract fraction rssi data
    max_left_rssinum = neighbor_level
    max_right_rssinum = neighbor_level
    index_beg = index_symbol - max_left_rssinum
    if index_beg < 0:
        index_beg = 0
    index_end = index_symbol + max_right_rssinum + 1
    if index_end > len(rssi_packet):
        index_end = len(rssi_packet)

    # calculate the corresponding training data of SINR for current symbol
    symbol_SINR = []
    for i in range(index_beg, index_end):
        isymbolrssi_dbm = RSSI_raw2dbm(rssi_packet[i])
        isymbolInterference_mw = dbm_to_mw(isymbolrssi_dbm) - signal_packet_mw - noise_mw
        symbol_SINR.append( signal_packet_mw/(isymbolInterference_mw + noise_mw) )

        print 'sinr-mw:%s, s:%s, i:%s, n:%s, rssi:%s' % (signal_packet_mw/(isymbolInterference_mw + noise_mw), signal_packet_mw, isymbolInterference_mw, noise_mw, rssi_packet[i])
        print 'sinr-dbm:%s, s:%s, i:%s, n:%s, rssi:%s' % (signal_packet_mw/(isymbolInterference_mw + noise_mw), mw_to_dbm(signal_packet_mw),mw_to_dbm(isymbolInterference_mw), mw_to_dbm(noise_mw), rssi_packet[i])
    return symbol_SINR


def calc_dif_RSSI(rssi_packet, rssi_selectfraction):
    # baseRSSI = int(max(rssi_packet,key=rssi_packet.count))
    baseRSSI = int(min(rssi_packet))

    for i in range(len(rssi_selectfraction)):
        rssi_selectfraction[i] = int(rssi_selectfraction[i]) - baseRSSI
    return rssi_selectfraction

# using multiple rssi value surrounded with data as input to training the model
# the rssi value still is the difference between the majority.
def RSSI_symbol_metrics(rssi_packet, index_data, neighbor_level):
    max_left_rssinum = neighbor_level
    max_right_rssinum = neighbor_level
    index_beg = index_data - max_left_rssinum
    if index_beg < 0:
        index_beg = 0
    index_end = index_data + max_right_rssinum + 1
    if index_end > len(rssi_packet):
        index_end = len(rssi_packet)
    return calc_dif_RSSI(rssi_packet, rssi_packet[index_beg:index_end])
    pass
