import rawDataExactor as rde
import math

# pilot_data: [ [data of pilot for input element],[RSSI, SNR]... ]
# pilot_ser :[ ser for each pilot, x1, ... ]
def onlineLearningMain(pilot_data, pilot_ser, theta):
	pilot_data =  normalize_pilotdata(pilot_data)
	theta = online_train(pilot_data, pilot_ser, theta)
	return theta
	pass


# calculate the square loss when using the update theta
def calc_loss(pilot_data, pilot_ser, theta):
	loss = 0
	for i in range(len(pilot_data)):
		df = destfunc(theta, pilot_data[i], pilot_ser[i])
		loss += df**2
	return loss/len(pilot_data)
	pass

# scale down the pilot data to [0,1]
def normalize_pilotdata(pilot_data):
	for i in range(len(pilot_data)):
		for j in range(len(pilot_data[i])):
			pilot_data[i][j] = int(pilot_data[i][j]) * 1.0 / 255
	return pilot_data
	pass

# p(y=0|x) = exp(-f(x))/ [ 1+ exp(-f(x)) ]
def destfunc(theta, pilot_data_i, pilot_ser_i):
	dis_fun = 0.0
	up_fun = theta[0]
	for j in range(1, len(theta)):
		up_fun += (theta[j] * pilot_data_i[j-1] )
	dis_fun = 1 / (1 + math.e**(up_fun))
	return pilot_ser_i - dis_fun
	pass

def adaplearnrate(learn_rate, pre_err_EMA, error_sum, pre_error_sum ,i,pilot_data_i, pre_pilot_data_i):
    #exponential moving average
    curEMA = (2* error_sum * error_sum + i * pre_err_EMA)/ (i+2)

    learn_rate[0]  = max(0.5, 1+ 0.8* (error_sum)* (pre_error_sum)/curEMA ) * learn_rate[0]
    for i in range(1, len(learn_rate)):
        learn_rate[i] = max(0.5, 1+ 0.8 * (error_sum * pilot_data_i[i-1]) * (pre_error_sum * pre_pilot_data_i[i-1]) /curEMA) * learn_rate[i]
    return [curEMA, learn_rate]


# pilot_data: [ [data of pilot for input element],[RSSI, SNR]... ]
# each of the support element has been scale down to [0, 1]
# pilot_ser :[ ser for each pilot, x1, ... ]
def online_train(pilot_data, pilot_ser, theta):
	
    loss = 10.0
    learn_rate = [0.001 for i in range(len(theta))]
    pre_err_EMA = 0
    pre_error_sum = 0


    # add in the first for multipling the constant variable
    # for i in range(len(pilot_data)):
    # 	pilot_data[i] = scaledown_pilotrssi()
    # 	for j in range(len(pilot_data[i])):


    for pIndex in range(len(pilot_data)):
        if loss <= 0.001: # if the loss rate is below 0.1%,
            break

        i = pIndex % len(pilot_data)
        error_sum = destfunc(theta, pilot_data[i], pilot_ser[i])
        # upda the learn rate

        [pre_err_EMA , learn_rate]= adaplearnrate(learn_rate, pre_err_EMA, error_sum, pre_error_sum ,i,pilot_data[i], pilot_data[i-1])
        pre_error_sum = error_sum
        # update the theta with the error sum and learn rate
        theta[0] += (learn_rate[0] * error_sum)
        for j in range(1, len(theta)):
            theta[j] += (learn_rate[j] * error_sum * pilot_data[i][j-1])

        # print "theta[0]:%s, theta[1]:%s\n" % (str(theta[0]) ,str(theta[1]))

        loss = calc_loss(pilot_data, pilot_ser, theta)

		# print "loss:%s\n" % (str(loss))
    print "finalLoss:%s, theta[0]:%s, theta[1]:%s\n" % (str(loss), str(theta[0]) ,str(theta[1]))
    return theta
    pass
