import rawDataExactor as rde
import math

# pilot_data: [ [data of pilot for input element],[RSSI, SNR]... ]
# pilot_ser :[ ser for each pilot, x1, ... ]
# a pilot data is a packet
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
# eliminate the the first 1.0 number
def normalize_pilotdata(pilot_data):
    for i in range(len(pilot_data)):
        for j in range(1, len(pilot_data[i])):
            pilot_data[i][j] = pilot_data[i][j] * 1.0 / 20
    return pilot_data
    pass

# p(y=0|x) = exp(-f(x))/ [ 1+ exp(-f(x)) ]
def destfunc(theta, pilot_data_i, pilot_ser_i):
    up_fun = 0
    for j in range(len(theta)):
        up_fun += (theta[j] * pilot_data_i[j])

    # up_fun = theta[0]
    # for j in range(1, len(theta)):
    #     up_fun += (theta[j] * pilot_data_i[j-1] )
    # dis_fun = 1 / (1 + math.e**(up_fun))

    dis_fun = math.e**(up_fun) / (1 + math.e**(up_fun))
    return pilot_ser_i - dis_fun
    pass

def adaplearnrate(learn_rate, pre_err_EMA, error_sum, pre_error_sum ,i,pilot_data_i, pre_pilot_data_i):
    #exponential moving average
    curEMA = (2* error_sum * error_sum + i * pre_err_EMA)/ (i+2)

    # learn_rate[0]  = max(0.5, 1+ 0.8* (error_sum)* (pre_error_sum)/curEMA ) * learn_rate[0]
    for i in range(len(learn_rate)):
        learn_rate[i] = max(0.5, 1+ 0.8 * (error_sum * pilot_data_i[i]) * (pre_error_sum * pre_pilot_data_i[i]) /curEMA) * learn_rate[i]
    return [curEMA, learn_rate]


# pilot_data: [ [data of pilot for input element],[RSSI, SNR]... ]
# each of the support element has been scale down to [0, 1]
# pilot_ser :[ ser for each pilot, x1, ... ]
def online_train(pilot_data, pilot_ser, theta):
    
    loss = 10.0
    learn_rate = [0.001 for i in range(len(theta))]
    deta_theta_avesquare = [0 for i in range(len(theta))]
    deta_theta = [0 for i in range(len(theta))]

    pre_err_EMA = 0
    pre_error_sum = 0
    max_iterate = len(pilot_data)
    # print pilot_data

    # add in the first for multipling the constant variable
    # for i in range(len(pilot_data)):
    #     pilot_data[i] = scaledown_pilotrssi()
    #     for j in range(len(pilot_data[i])):


    for pIndex in range(max_iterate):
        if loss <= 0.001: # if the loss rate is below 0.1%,
            break

        i = pIndex % len(pilot_data)

        error_sum = destfunc(theta, pilot_data[i], pilot_ser[i])

        ''' papers way'''
        for ti in range(len(theta)):
            deta_theta_pre = deta_theta[ti]
            deta_theta[ti] = error_sum * pilot_data[i][ti]


            deta_theta_avesquare[ti] = (2 * deta_theta[ti] * deta_theta[ti] + i * deta_theta_avesquare[ti])/(i+2)
            '''sensys12 - update the expon moving average'''
            # deta_theta_avesquare[ti] = 0.8 * deta_theta_avesquare[ti] + 0.2 * (deta_theta[ti] ** 2)
            if deta_theta_avesquare[ti] != 0:
                learn_rate[ti] = learn_rate[ti] * max( 0.5 , 1 + 0.8 *
                        (deta_theta_pre * deta_theta[ti] / deta_theta_avesquare[ti]))

            ''''simple way to update the learning rate'''
            # learn_rate[thetaIndex] =


            theta[ti] = theta[ti] + learn_rate[ti] * deta_theta[ti]

            # print theta


        # # upda the learn rate
        # [pre_err_EMA , learn_rate]= adaplearnrate(learn_rate, pre_err_EMA, error_sum, pre_error_sum ,i,pilot_data[i], pilot_data[i-1])
        # pre_error_sum = error_sum
        # # update the theta with the error sum and learn rate
        # # theta[0] += (learn_rate[0] * error_sum)
        # for j in range(len(theta)):
        #     theta[j] += (learn_rate[j] * error_sum * pilot_data[i][j])

        # print '[%s]' % (pIndex), pilot_data[i]
        # print "theta[0]:%s, theta[1]:%s\n" % (str(theta[0]) ,str(theta[1]))

        loss = calc_loss(pilot_data, pilot_ser, theta)
        # print_theta(theta, loss)
        # print "loss:%s\n" % (str(loss))
    return theta
    pass

def print_theta(theta, loss):
    print "finalLoss:%s," % (str(loss)),
    for i in range(len(theta)):
        print 'theta[%d]:%s,' % (i,str(theta[i])),
    print ''
    pass
