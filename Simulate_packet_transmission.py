import Pilot_data_simulate as pds
import SSER_online_train as ot
import math
import Gnuplot_related as gr
import rawDataExactor as rde

# groundtruth that true is 0% determine the, false is 100%
# def groudtruth(unkonwSymbolp, limit_length):
#     gt_ser_all = []
#     for i in range(limit_length):
#         gt_ser_packet = []
#         for j in range(len(unkonwSymbolp[i])):
#             if unkonwSymbolp[i][j] != '0':
#                 gt_ser_packet.append(0.1)
#             else:
#                 gt_ser_packet.append(0.99)
#         gt_ser_all.append(gt_ser_packet)
#     return gt_ser_all
#     pass

def estimate_ser(pilot_data_alltrace, pilot_ser_alltrace, other_data_alltrace, limit_length, theta_num):
    theta = [2 for i in range(theta_num)]
    est_ser_all = []
    # for i in range(len(pilot_data_alltrace)):


    for i in range(limit_length[0], limit_length[1]):
        # theta = [1 for j in range(len(pilot_data_alltrace[0][0])+ 1)]

        # print '%s', pilot_data_alltrace[i]
        theta = ot.onlineLearningMain(pilot_data_alltrace[i], pilot_ser_alltrace[i], theta)
        est_ser_packet = []
        nor_other_data_packet = ot.normalize_pilotdata(other_data_alltrace[i])

        # estimate new algorithm
        for j in range(len(nor_other_data_packet)):
            up_fun = 0
            for k in range(len(theta)):
                up_fun += (theta[k] * nor_other_data_packet[j][k])
                # print 'theta[%s]%s' % (k , theta[k] * int(nor_other_data_packet[j][k-1])),
            # dis_fun = 1 / (1 + math.e**(up_fun))
            dis_fun = math.e**(up_fun) / (1 + math.e**(up_fun))
            est_ser_packet.append(dis_fun)


        # estimate every symbol error rate except the pilot
        # for j in range(len(nor_other_data_packet)):
        #     up_fun = theta[0]
        #     for k in range(1, len(theta)):
        #         up_fun += (theta[k] * nor_other_data_packet[j][k-1])
        #         # print 'theta[%s]%s' % (k , theta[k] * int(nor_other_data_packet[j][k-1])),
        #     # dis_fun = 1 / (1 + math.e**(up_fun))
        #     dis_fun = math.e**(up_fun) / (1 + math.e**(up_fun))
        #     est_ser_packet.append(dis_fun)
            # print '[%s-%s]' %(i,j), nor_other_data_packet[j], \
            #     '[%s/(1+%s)] = %s' % (math.e**(up_fun), math.e**(up_fun), dis_fun)

        # print "[%d]:" % (i), est_ser_packet, '\n'
        est_ser_all.append(est_ser_packet)
    return est_ser_all
    pass



def Calc_metric(est_ser, unkonwSymbolp,limit_length):
    accur_alltrace = []
    detailAccur_alltrace = []

    for i in range(len(est_ser)):
        fp=0;fn=0;tp=0;tn=0
        accru_packet = []
        detailAccur_packet = []
        for j in range(len(est_ser[i])):
            # print unkonwSymbolp[i][j], est_ser[i][j]
            if est_ser[i][j] > 0.5:
                if unkonwSymbolp[i+limit_length[0]][j] != '0':
                    tn += 1
                else:
                    fn += 1
            else:
                if unkonwSymbolp[i+ limit_length[0]][j] == '0':
                    tp += 1
                else:
                    fp += 1
        detailAccur_packet.append(fp)
        detailAccur_packet.append(fn)
        detailAccur_packet.append(tp)
        detailAccur_packet.append(tn)
        detailAccur_alltrace.append(detailAccur_packet)

        if tp + fp != 0:
            tp_precision = (tp) * 1.0/ (tp+fp)
        else:
            tp_precision = 0
        if tn + fn != 0 :
            tn_precision = (fn) * 1.0 /(tn+fn)
        else:
            tn_precision = 0

        if tp+fp+tn+fn != 0:
            precision = (tn+tp)*1.0 / (tp+fp+tn+fn)# accuracy
        else:
            precision = 0
        if tn+fp != 0:
            tn_recall = tn*1.0 / (tn+fp)    # whole
        else:
            tn_recall = 0
        if tp+ fn != 0:
            tp_recall = (tp)*1.0/ (tp+fn)
        else:
            tp_recall = 0
        accru_packet.append(precision)
        accru_packet.append(tp_recall)
        accru_packet.append(tn_recall)
        accru_packet.append(tp_precision)
        accru_packet.append(tn_precision)
        accur_alltrace.append(accru_packet)
    return [accur_alltrace, detailAccur_alltrace]

def print_detail_result(est_ser, UnkonwSymbolPayload,other_data_alltrace, limit_length,metric_command ):
    result = []
    for i in range(len(est_ser)):
        for j in range(len(est_ser[i])):
            metric_list = []
            for k in range(len(other_data_alltrace[i][j])):
                metric_list.append('[%s]%s' % (k,other_data_alltrace[i][j][k]))
            metric_data = ','.join(metric_list)

            result.append("[%d-%d][est]:%s, [payload]:%s, [Metric-%s]:%s \n" %
                          (i,j, str(est_ser[i][j]) ,
                           str(UnkonwSymbolPayload[i+limit_length[0]][j]),
                           metric_command,metric_data))
    f =open('figure/result_%d_%d_%s.txt' % (limit_length[0],limit_length[1], metric_command),'w')
    f.writelines(result)
    f.close()
    pass

def print_split_trace(split_data, split_rssi,  pilot_step, limit_length):
    trace = []
    # [split_data, split_rssi, pilot_step] = pds.simulated_tracebase(False)
    [raw_data, raw_rssi] = rde.readTrace(  "rx-0-22-11-20140629-15-47-41-with_interference_802.11g")
    for i in range(limit_length[0], limit_length[1]):
        for j in range(len(split_rssi[i])):
            rawrssi = 0
            if j >= len(raw_rssi[i]):
                rawrssi = -1
            else:
                rawrssi = raw_rssi[i][j]
            if j% pilot_step != 0:
                trace.append("[%d-%d][raw_rssi]:%s, [spredRSSI]:%s, [raw_data]:%s\n" % (i,j,rawrssi, split_rssi[i][j],split_data[i][j]))
            else:
                trace.append("[pilot][%d-%d][raw_rssi]:%s, [spredRSSI]:%s, [raw_data]:%s\n" % (i,j,rawrssi, split_rssi[i][j], split_data[i][j]))


    f = open("figure/rssi_compare_%d_%d.txt" % (limit_length[0], limit_length[1]),'w')
    f.writelines(trace)
    f.close()
    pass



def algortihmtest(metric_c, argvL):
    limit_length = [0,30]

    metric_command = metric_c
    argvList = argvL
    [split_data, split_rssi, pilot_step] = pds.simulated_tracebase(metric_command, argvList)
    [pilot_data_alltrace, pilot_ser_alltrace] = pds.simulated_pilot_generate(split_data, split_rssi, pilot_step, metric_command, argvList)
    other_data_alltrace = pds.simulated_unkonw_symbol(split_data, split_rssi, pilot_step, metric_command, argvList)
    unkonwSymbolp = pds.UnkonwSymbolPayload(split_data, pilot_step)


    # print len(split_data), len(split_rssi), len(pilot_data_alltrace), len(pilot_ser_alltrace), len(other_data_alltrace), len(unkonwSymbolp)
    print '[+]start est_ser'
    est_ser = estimate_ser(pilot_data_alltrace, pilot_ser_alltrace, other_data_alltrace, limit_length, argvList[0] * 2 +1)
    # print 'start gt_ser'
    # gt_ser = groudtruth(unkonwSymbolp, limit_length)
    # print 'rstart rt_err'
    # print '[est]',len(est_ser[0]), '[gt]:', len(gt_ser[0])
    # rt_err = relatederror(est_ser, gt_ser)
    # for i in range(len(rt_err)):
    #     print "%d:" % (i), rt_err[i][len(rt_err[i])-1]



    # print '[debug]write no diff rssi data trace'
    other_nodiff_data_trace = pds.simulated_unkonw_symbol(split_data, split_rssi, pilot_step, metric_command, argvList)
    gr.print_gnuplot(est_ser, unkonwSymbolp,other_nodiff_data_trace,limit_length)

    # print '[debug]write detailed result'
    print_detail_result(est_ser, unkonwSymbolp, other_nodiff_data_trace, limit_length,metric_command)

    # print '[debug]print rssi info'
    print_split_trace(split_data, split_rssi, pilot_step, limit_length)

    # print "[!]calc metric"
    [accur_alltrace, detailAccur_alltrace] = Calc_metric(est_ser, unkonwSymbolp,limit_length)
    ave_tppreci = 0; ave_tnpreci = 0; avetn_recall = 0
    for i in range(len(accur_alltrace)):
        # print "%d:[preci]%s, [tp_rec]:%s,[tn_rec]%s, [tp_pre]%s, [tn_pre]%s" %\
        #       (i, str(accur_alltrace[i][0]), accur_alltrace[i][1],
        #        str(accur_alltrace[i][2]), str(accur_alltrace[i][3]), str(accur_alltrace[i][4])),

        # print "[fp]:%s, [fn]:%s, [tp]:%s, [tn]:%s" % (str(detailAccur_alltrace[i][0]),str(detailAccur_alltrace[i][1]),str(detailAccur_alltrace[i][2]),str(detailAccur_alltrace[i][3]) )
        ave_tppreci += accur_alltrace[i][3]
        ave_tnpreci += accur_alltrace[i][4]
        avetn_recall += accur_alltrace[i][2]

    print '[metrics]:%s_%s{%s-%s}, [ave_tpprecision]:%s,  [ave_tnpreci]%s,  [ave_tnrecall]:%s' % \
          ( limit_length[0], limit_length[1],
              metric_command, str(argvList[0]),
            str(ave_tppreci/len(accur_alltrace)),   str(ave_tnpreci/ len(accur_alltrace)),  str(avetn_recall/len(accur_alltrace)))


if __name__ == '__main__':

    metric_command_readytest = ["SINR", "RSSI"]
    argvList = [0,1,2]
    algortihmtest(metric_command_readytest[0], [argvList[1]])
    # for mc in metric_command_readytest:
    #     for al in argvList:
    #         algortihmtest(mc, [al])

    pass


#
# def relatederror(est_ser, gt_ser):
#     rt_error_all = []
#     for i in range(len(est_ser)):
#         rt_error_packet = []
#         sumerror = 0
#         # print len(est_ser[i])
#         for j in range(len(est_ser[i])):
#             # print j
#             # rt = (est_ser[i][j] - gt_ser[i][j]) / (gt_ser[i][j])
#             rt = abs(est_ser[i][j] - gt_ser[i][j])
#             sumerror += rt
#             rt_error_packet.append(rt)
#         rt_error_packet.append(sumerror/len(est_ser[i]))# the last element is the average related error
#         rt_error_all.append(rt_error_packet)
#     return rt_error_all
#     pass