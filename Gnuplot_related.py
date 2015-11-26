import rawDataExactor as rde
import Pilot_data_simulate as pds


def allrssitrace():
    [split_data, split_rssi, pilot_step] = pds.simulated_tracebase(True)
    intofile = []
    for i in range(34,35):
        tempstr = []
        for j in range(len(split_data[i])):
            tempstr.append('%d ' % (j))
            if split_data[i][j] == '0':
                tempstr.append('210 ')
            else:
                tempstr.append('245 ')
            ft = split_rssi[i][j]
            tempstr.append(str(ft) + '\n')
        intofile.extend(''.join(tempstr))

    # [dataTrace, rssiTrace] = scaledRSSI(dataTrace, rssiTrace)
    f = open('rssi_data.txt', 'w')
    f.writelines(intofile)
    f.close()



# [position],[tn],[fn],[tp],[fp]
def print_gnuplot(est_ser, unkonwSymbolp,other_data_alltrace):
    intofile = []
    wholecounter = 1
    for i in range(len(est_ser)):
        for j in range(len(est_ser[i])):
            eachline = [str(wholecounter) + ' ']
            if est_ser[i][j] > 0.5 :
                if unkonwSymbolp[i][j] != '0':
                    eachline.append(str(other_data_alltrace[i][j][0]) + ' 0 0 0')
                else:
                    eachline.append('0 ' + str(other_data_alltrace[i][j][0]) + ' 0 0')
            else:
                if unkonwSymbolp[i][j] == '0':
                    eachline.append('0 0 ' + str(other_data_alltrace[i][j][0]) + ' 0')
                else:
                    eachline.append('0 0 0 ' + str(other_data_alltrace[i][j][0]))
            intofile.append(''.join(eachline) + '\n')
            wholecounter += 1
    f = open('TFdiag_data_11_20.txt','w')
    f.writelines(intofile)
    f.close()
    pass

# if __name__ == '__main__':
#     allrssitrace()
    #
    # [split_data, split_rssi, pilot_step] = pds.simulated_tracebase()
    # intofile = []
    # for i in range(len(split_data)):
    #     tempstr = []
    #     for j in range(len(split_data[i])):
    #         if split_data[i][j] == '0':
    #             tempstr.append('-1 ')
    #         else:
    #             tempstr.append('1 ')
    #         tempstr.append(split_rssi[i][j] + '\n')
    #     intofile.extend(''.join(tempstr))
    #
    # f = open('rssi_data.txt', 'w')
    # f.writelines(intofile)
    # f.close()
    # pass