import ClientHistoryReadout as chis
import UsefulFunctionsClient as uf
import datetime as dt

def split(data):
    dates = data[0::2]
    datapoints = data[1::2]

    for i in range(len(datapoints)):
        datapoint = datapoints[i].replace("'","")
        datapoints[i] = float(datapoint)

    for i in range(len(dates)):
        dates[i] = dt.datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S.%f")

    return dates, datapoints

array = chis.getHistory_duration("Pressure", 48)
x, y = split(array)
print x, y

for j in range(len(y)):
	if y[j] != -20.0:
		print x[j]
		print y[j]
