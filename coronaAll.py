import re
import requests

import plotly
import plotly.graph_objects as go

import datetime
from datetime import date, timedelta

import plotly.express as px



# Gets all links in the JHU CSSEGI repo for daily reports

linkall = []

# datalink = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
# datareq = requests.get(datalink)

# htmldata = datareq.text

# htmlpattern = re.compile("<a class=\"js-navigation-open \" [^>]+")

# appearances = htmlpattern.findall(htmldata)

# for u in appearances[1:-1]:
#     rawurl = u.split(" ")[5]
#     url = "https://raw.githubusercontent.com" + rawurl[6:31] + rawurl[36:-1]
#     linkall.append(url)

dayrange = (date.today() - date(2020, 1, 22)).days

day = date(2020, 1, 22)

for d in range(0, dayrange):
    daystr = day.strftime("%m-%d-%Y")
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + daystr + ".csv"
    linkall.append(url)
    day += datetime.timedelta(days=1)

# Gets data from january 22 to march 9


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


# Gets data from march 10 to march 21

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


alldata = {}
maxinfected = []
maxdead = []

statesdict = {"Massachusetts" : "MA", "New York" : "NY", "California" : "CA", "Washington" : "WA"}

for name,abbr in statesdict.items():
    datapt1 = getCorona(abbr)
    datapt2 = getData1(name)
    datapt3 = getInfected(name)


    alldata[abbr] = [datapt1[0] + datapt2[0] + datapt3[0], datapt1[1] + datapt2[1] + datapt3[1]]
    if abbr == "NY":
      maxinfected.append(max(alldata[abbr][0])/10)
    else:
      maxinfected.append(max(alldata[abbr][0]))
    maxdead.append(max(alldata[abbr][1]))


fram = []
framd = []

#scalemax = 0

#print(alldata)


datescale = [date(2020, 1, 22)]


for d in range(len(linkall)-1):
  datescale.append(datescale[-1] + timedelta(days=1))

#print(datescale)

# alldata["NY"][0] = [x//10 for x in alldata["NY"][0]]
#alldata["New York"][1] = [x//5 for x in alldata["New York"][1]]


for x in range(0, len(linkall)-40):
  state1name = "MA"
  state2name = "NY"
  state3name = "CA"
  state4name = "WA"

  state1 = go.Scatter(x=datescale[40:40+x], y=alldata[state1name][0][40:], mode="lines+markers", marker_symbol="cross", marker_size=7, name = state1name + " Infected", line_width = 2)
  state2 = go.Scatter(x=datescale[40:40+x], y=alldata[state2name][0][40:], mode="lines+markers", marker_symbol="x", marker_size=7, name = state2name + " Infected (divided by 10)", line_width = 2)
  state3 = go.Scatter(x=datescale[40:40+x], y=alldata[state3name][0][40:], mode="lines+markers", marker_symbol="circle", marker_size=7, name = state3name + " Infected", line_width = 2)
  state4 = go.Scatter(x=datescale[40:40+x], y=alldata[state4name][0][40:], mode="lines+markers", marker_symbol="triangle-up", marker_size=7, name = state4name + " Infected", line_width = 2)

  state1D = go.Scatter(x=datescale[40:40+x], y=alldata[state1name][1][40:], mode="lines+markers", marker_symbol="cross", marker_size=7, name = state1name + " Deaths", line_width = 2, line_color = "#1f77b4")
  state2D = go.Scatter(x=datescale[40:40+x], y=alldata[state2name][1][40:], mode="lines+markers", marker_symbol="x", marker_size=7, name = state2name + " Deaths", line_width = 2, line_color = "#d62728")
  state3D = go.Scatter(x=datescale[40:40+x], y=alldata[state3name][1][40:], mode="lines+markers", marker_symbol="circle", marker_size=7, name = state3name + " Deaths", line_width = 2, line_color = "#2ca02c")
  state4D = go.Scatter(x=datescale[40:40+x], y=alldata[state4name][1][40:], mode="lines+markers", marker_symbol="triangle-up", marker_size=7, name = state4name + " Deaths", line_width = 2, line_color = "#9467bd")


  allstates = [state1, state2, state3, state4, state1D, state2D, state3D, state4D]
  #allstatesD = [state1D, state2D, state3D, state4D]

  fram.append(go.Frame(data=allstates, traces=list(range(len(allstates))), layout = {"annotations" : [
        dict(
            x=datescale[40+x-1],
            y=alldata[state1name][0][40+x-1],
            xref="x",
            yref="y",
            text=str(alldata[state1name][0][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=30,
            ay=-10, 
            bgcolor="#1f77b4"), 
        dict(
            x=datescale[40+x-1],
            y=alldata[state2name][0][40+x-1],
            xref="x",
            yref="y",
            text=str(alldata[state2name][0][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=20,
            ay=-40, 
            bgcolor="#d62728"), 
        dict(
            x=datescale[40+x-1],
            y=alldata[state3name][0][40+x-1],
            xref="x",
            yref="y",
            text=str(alldata[state3name][0][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=90,
            ay=-60, 
            bgcolor="#2ca02c"), 
        dict(
            x=datescale[40+x-1],
            y=alldata[state4name][0][40+x-1],
            xref="x",
            yref="y",
            text=str(alldata[state4name][0][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=60,
            ay=-10,
            bgcolor="#9467bd"),    
        dict(
            x=datescale[40+x-1],
            y=alldata[state1name][1][40+x-1],
            xref="x2",
            yref="y2",
            text=str(alldata[state1name][1][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=80,
            ay=-40, 
            bgcolor="#1f77b4"),
        dict(
            x=datescale[40+x-1],
            y=alldata[state2name][1][40+x-1],
            xref="x2",
            yref="y2",
            text=str(alldata[state2name][1][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=-40,
            ay=-40, 
            bgcolor="#d62728"), 
        dict(
            x=datescale[40+x-1],
            y=alldata[state3name][1][40+x-1],
            xref="x2",
            yref="y2",
            text=str(alldata[state3name][1][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=60,
            ay=-40, 
            bgcolor="#2ca02c"), 
        dict(
            x=datescale[40+x-1],
            y=alldata[state4name][1][40+x-1],
            xref="x2",
            yref="y2",
            text=str(alldata[state4name][1][40+x-1]),
            showarrow=True,
            arrowhead=7,
            ax=30,
            ay=-40, 
            bgcolor="#9467bd")]}))
  #framd.append(go.Frame(data=allstatesD, traces=list(range(len(allstates)))))

# shorten legend
# text color in annotations
# box color in annotations
# add descriptions maybe




dayscale = len(list(alldata.values())[0][0]) - 32


print(maxinfected)

ymax = int(max(maxinfected) * 1.1)
ymaxD = int(max(maxdead) * 1.1)


#fig = make_subplots(rows=1, cols=2)




figI = go.Figure(
    data=[go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x1', yaxis='y1'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x1', yaxis='y1'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x1', yaxis='y1'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x1', yaxis='y1'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x2', yaxis='y2'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x2', yaxis='y2'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x2', yaxis='y2'), 
    go.Scatter(x=datescale[40:42], y=[0, 0], xaxis='x2', yaxis='y2')],
    layout=go.Layout(
        xaxis1=dict(range=[datescale[40], datescale[-1]], autorange=False, title="Date", domain = [0.0, 0.44], anchor = 'y1'),
        yaxis1=dict(range=[0, ymax], title="People Infected by the Coronavirus", domain = [0.0, 1.0], anchor = 'x1'),
        xaxis2=dict(range=[datescale[40], datescale[-1]], autorange=False, title="Date", domain = [0.56, 1.0], anchor = 'y2'),
        yaxis2=dict(range=[0, ymaxD], title="People Dead by the Coronavirus", domain = [0.0, 1.0], anchor = 'x2'),
        title="Coronavirus Infections and Deaths since March 2, 2020",
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 100, "redraw": True}, 'transition': {'duration': 100}}])])]
    ),
)


'''
figD = go.Figure(
    data=[go.Scatter(x=datescale[40:42], y=[0, 0]), go.Scatter(x=datescale[40:42], y=[0, 0]), go.Scatter(x=datescale[40:42], y=[0, 0]), go.Scatter(x=datescale[40:42], y=[0, 0])],
    layout=go.Layout(
        xaxis=dict(range=[datescale[40], datescale[-1]], autorange=False, title="Date"),
        yaxis=dict(range=[0, ymaxD], title="People Infected by the Coronavirus"),
        title="Start Title",
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 700, "redraw": True}, 'transition': {'duration': 700}}])])]
    ),
)
'''



figI.update(frames = fram)
"""
figI.update_layout(annotations=[
        dict(
            x=datetime(2020, 1, 22),
            y=21,
            xref="x",
            yref="y",
            text="dict Text",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    ])
"""

#figD.update(frames = framd)
figI.write_html("coronaAug.html", auto_open = True)
# figI.show()
#figD.show()

#fig =px.scatter(x=range(10), y=range(10))


