import Pilot_data_simulate as pds
import SSER_online_train as ot
import math
import Gnuplot_related as gr

# groundtruth that true is 0% determine the, false is 100%
def groudtruth(unkonwSymbolp, limit_length):
	gt_ser_all = []
	for i in range(limit_length):
		gt_ser_packet = []  
		for j in range(len(unkonwSymbolp[i])):
			if unkonwSymbolp[i][j] != '0':
				gt_ser_packet.append(0.1)
			else:
				gt_ser_packet.append(0.99)
		gt_ser_all.append(gt_ser_packet)
	return gt_ser_all
	pass

def estimate_ser(pilot_data_alltrace, pilot_ser_alltrace, other_data_alltrace, limit_length):
	theta = [1 for i in range(len(pilot_data_alltrace[0][0])+ 1)]
	est_ser_all = []
	# for i in range(len(pilot_data_alltrace)):
	for i in range(limit_length):
		# theta = [1 for j in range(len(pilot_data_alltrace[0][0])+ 1)]

		theta = ot.onlineLearningMain(pilot_data_alltrace[i], pilot_ser_alltrace[i], theta)
		est_ser_packet = []
		# estimate every symbol error rate except the pilot
		for j in range(len(other_data_alltrace[i])):
			up_fun = theta[0]
			for k in range(1, len(theta)):
				up_fun += (theta[k] * int(other_data_alltrace[i][j][k-1]))
			dis_fun = 1 / (1 + math.e**(up_fun))
			est_ser_packet.append(dis_fun)
		# print "[%d]:" % (i), est_ser_packet, '\n'
		est_ser_all.append(est_ser_packet)
	return est_ser_all
	pass

def relatederror(est_ser, gt_ser):
	rt_error_all = []
	for i in range(len(est_ser)):
		rt_error_packet = []
		sumerror = 0
		# print len(est_ser[i])
		for j in range(len(est_ser[i])):
			# print j
			# rt = (est_ser[i][j] - gt_ser[i][j]) / (gt_ser[i][j])
			rt = abs(est_ser[i][j] - gt_ser[i][j])
			sumerror += rt
			rt_error_packet.append(rt)
		rt_error_packet.append(sumerror/len(est_ser[i]))# the last element is the average related error
		rt_error_all.append(rt_error_packet)
	return rt_error_all
	pass


def Calc_metric(est_ser, unkonwSymbolp):
    accur_alltrace = []
    detailAccur_alltrace = []

    for i in range(len(est_ser)):
        fp=0;fn=0;tp=0;tn=0
        accru_packet = []
        detailAccur_packet = []
        for j in range(len(est_ser[i])):
            # print unkonwSymbolp[i][j], est_ser[i][j]
            if est_ser[i][j] > 0.5:
                if unkonwSymbolp[i][j] != '0':
                    tn += 1
                else:
                    fn += 1
            else:
                if unkonwSymbolp[i][j] == '0':
                    tp += 1
                else:
                    fp += 1
        detailAccur_packet.append(fp)
        detailAccur_packet.append(fn)
        detailAccur_packet.append(tp)
        detailAccur_packet.append(tn)
        detailAccur_alltrace.append(detailAccur_packet)

        if tn+fn != 0:
            precision = tn*1.0 / (tn+fn)# accuracy
        else:
            precision = 0
        if tp+fn != 0:
            recall = tn*1.0 / (tn+fp)    # whole
        else:
            recall = 0
        accru_packet.append(precision)
        accru_packet.append(recall)
        accur_alltrace.append(accru_packet)
    return [accur_alltrace, detailAccur_alltrace]



if __name__ == '__main__':
    [split_data, split_rssi, pilot_step] = pds.simulated_tracebase(True)
    [pilot_data_alltrace, pilot_ser_alltrace] = pds.simulated_pilot_generate()
    other_data_alltrace = pds.simulated_unkonw_symbol(True)
    unkonwSymbolp = pds.UnkonwSymbolPayload()


    # print len(split_data), len(split_rssi), len(pilot_data_alltrace), len(pilot_ser_alltrace), len(other_data_alltrace), len(unkonwSymbolp)
    limit_length = 10
    print 'start est_ser'
    est_ser = estimate_ser(pilot_data_alltrace, pilot_ser_alltrace, other_data_alltrace, limit_length)
    # print 'start gt_ser'
    # gt_ser = groudtruth(unkonwSymbolp, limit_length)
    # print 'rstart rt_err'
    # print '[est]',len(est_ser[0]), '[gt]:', len(gt_ser[0])
    # rt_err = relatederror(est_ser, gt_ser)
    # for i in range(len(rt_err)):
    # 	print "%d:" % (i), rt_err[i][len(rt_err[i])-1]

    other_nodiff_data_trace = pds.simulated_unkonw_symbol(False)
    gr.print_gnuplot(est_ser, unkonwSymbolp,other_nodiff_data_trace)
    print "calc metreic"
    [accur_alltrace, detailAccur_alltrace] = Calc_metric(est_ser, unkonwSymbolp)
    for i in range(len(accur_alltrace)):
        print "%d:[preci]%s, [recall]:%s" % (i, str(accur_alltrace[i][0]), accur_alltrace[i][1]),
        print "[fp]:%s, [fn]:%s, [tp]:%s, [tn]:%s" % (str(detailAccur_alltrace[i][0]),str(detailAccur_alltrace[i][1]),str(detailAccur_alltrace[i][2]),str(detailAccur_alltrace[i][3]) )

pass
