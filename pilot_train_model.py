import rawDataExactor as rde
'''
This model is used to train the pilot CDF.
The output maybe two curve graph: 
one is "consistently biased bit vs consistently Theoretic memoryless bit",
the other is "bursty biased bit vs bursty Theoretic memoryless bit".

The actual x-coordinate and y-coordinate for histogram.
For the first, x is "consistently biased bit burst length", 
y is "the times that can ensure the bit is fixed using corresponding burst length".
For the second, x, y is similiar. 

'''

def test():
    [dataTrace, rssiTrace] = rde.readTrace("rx-0-22-11-20140629-15-47-41-with_interference_802.11g")
    print len(dataTrace[2]),dataTrace[1],type(dataTrace[1][2])
    print len(rssiTrace[4]),rssiTrace[4]
    pass

test()
