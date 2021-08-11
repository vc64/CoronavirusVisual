import re
import requests

import datetime
from datetime import date, timedelta

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates

# Gets all links in the JHU CSSEGI repo for daily reports

linkall = []


dayrange = (date.today() - date(2020, 1, 22)).days

day = date(2020, 1, 22)

for d in range(0, dayrange):
    daystr = day.strftime("%m-%d-%Y")
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + daystr + ".csv"
    linkall.append(url)
    day += datetime.timedelta(days=1)


# Gets data from january 22 to march 9 (due to different formats)

def getCorona(state):
    infect = []
    death = []
    for link in linkall[0:48]:
        req = requests.get(link)

        reqtext = req.text


        pattern = re.compile(state + "[^\n]+")

        matches = pattern.findall(reqtext)

        totalcountyinfect = 0
        totalcountydead = 0
        for county in matches:
            countydata = county.split(",")
            totalcountyinfect += int(countydata[3])
            totalcountydead += int(countydata[4])

        infect.append(totalcountyinfect)
        death.append(totalcountydead)

    return(infect, death)


# Gets data from march 10 to march 21 (due to different formats)

def getData1(state):
    infect = []
    death = []
    for link in linkall[49:60]:
        statereq = requests.get(link)

        statetext = statereq.text

        patternRE = re.compile(state + ".+\n")

        statedata = patternRE.findall(statetext)[0]

        statevalues = statedata.split(",")

        infect.append(int(statevalues[3]))
        death.append(int(statevalues[4]))

    return [infect, death]


# Gets data from march 22 to most recent

def getInfected(state):
    infect = []
    death = []
    for link in linkall[60:]:
        data = requests.get(link)

        dataText = data.text
        
        
        patternRE = re.compile(",[a-zA-Z\s\.]+," + state + "[^\"]*\"")

        dataState = patternRE.findall(dataText)


        provinces = []

        for x in dataState:
            dataProvince = x.split(",")
            provinces.append(dataProvince)

        
        totalInf = 0
        totaldead = 0

        for p in provinces:
            totalInf += int(p[7])
            totaldead += int(p[8])

        infect.append(totalInf)
        death.append(totaldead)

    return [infect, death]


# use above functions to get and store all the data in dictionary

alldata = {}
maxinfected = []
maxdead = []

statesdict = {"Massachusetts" : "MA", "New York" : "NY", "California" : "CA", "Washington" : "WA"}

for name,abbr in statesdict.items():
    datapt1 = getCorona(abbr)
    datapt2 = getData1(name)
    datapt3 = getInfected(name)


    alldata[abbr] = [datapt1[0] + datapt2[0] + datapt3[0], datapt1[1] + datapt2[1] + datapt3[1]]
    
    maxinfected.append(max(alldata[abbr][0]))
    maxdead.append(max(alldata[abbr][1]))


# plotting and animating the data with matplotlib

fig, (axI, axD) = plt.subplots(1, 2, figsize = (8, 6))

plt.style.use("default")
# fig.set_facecolor("w")

three_month = mdates.MonthLocator(interval=3)
axI.xaxis.set_major_locator(three_month)
axI.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))

axD.xaxis.set_major_locator(three_month)
axD.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))


dates = mdates.date2num(datescale)
fig.tight_layout(pad=3.0)
plt.gcf().autofmt_xdate()
axD = fig.add_axes([0.1, 0.1, 0.6, 0.75])
# plt.figure(num=1, figsize=(30, 30))

linesI = []
linesD = []

xdataAll = []
ydataAllI = []
ydataAllD = []

for name,abbr in statesdict.items():
    linesI.append(axI.plot_date(dates[0], 0, linewidth = 2, linestyle='solid', marker='None')[0])
    linesD.append(axD.plot_date(dates[0], 0, linewidth = 2, linestyle='solid', marker='None')[0])
    
    xdataAll.append([])
    ydataAllI.append([])
    ydataAllD.append([])


def animate(i):
    
    index = 0
    
    for name,abbr in statesdict.items():
        xdataAll[index].append(dates[i])
        ydataAllI[index].append(alldata[abbr][0][i])
        ydataAllD[index].append(alldata[abbr][1][i])
        
        
        linesI[index].set_data(xdataAll[index], ydataAllI[index])
        linesD[index].set_data(xdataAll[index], ydataAllD[index])
        
        index += 1
    
    return linesI + linesD


ymaxI = int(max(maxinfected) * 1.1)
ymaxD = int(max(maxdead) * 1.1)


axI.set_ylim(0, ymaxI)
axI.set_xlim(dates[0], dates[-1])

axD.set_ylim(0, ymaxD)
axD.set_xlim(dates[0], dates[-1])

axI.set_ylabel("Infected")
axD.set_ylabel("Deaths")
fig.suptitle("Infections and Deaths from COVID-19 in the United States")
plt.legend(linesI, list(statesdict.keys()), loc = "center left", bbox_to_anchor = (1, 0.8))

# plt.show()

anim = animation.FuncAnimation(fig, animate, frames=len(alldata["MA"][0]), interval=20, blit=True, repeat=False)



anim.save("coronaAug2021.gif", writer='Pillow')