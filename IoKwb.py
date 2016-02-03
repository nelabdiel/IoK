import os
from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup
import math
import pickle
import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.util.string import encode_utf8
import dill


app = Flask(__name__)

app.vars = {}

################################################
# world records data
###############################################
class Company(object):
    def __init__(self, worldrec):
        self.worldrec = worldrec      
with open('worldrecords_data.pkl', 'rb') as f:
    wrdatar = pickle.load(f)    

records = wrdatar.worldrec

###############################################
# recent competitions data
###############################################
#class Company(object):
#    def __init__(self, rec):
#        self.rec = rec
#with open('recent_comp.pkl', 'rb') as input:
#    rdatar = pickle.load(input, encoding='latin1')    

#recent_data = rdatar.rec  


################################################
# predictive model
###############################################
class Company1(object):
    def __init__(self, mod):
        self.mod = mod
with open('nei_model.pkl', 'rb') as input:
    nei_model_predict = pickle.load(input)    

nei_model_pred = nei_model_predict.mod


#Nel-Sinclair Curve
a = 85.477722914300003
b = 41.357074003999998
c = 0.0060825625000000003
d = 512.45085465119996
#Nel-Sinclair Function    
def approx(x): 
    return a*np.log(c*(x-b))+d

#Index page
@app.route('/')
def main():
    return redirect('/index')


############################################################################
#Homepage
############################################################################
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
        
############################################################################    
#Nel-Sinclair Page
############################################################################
@app.route('/nsc', methods=['GET', 'POST'])
def NSC():
    
        #World Records
    bw = [55.62, 61.81, 68.68, 76.4, 84.69, 93.52, 104.76, 147.48]
    total = [305, 332, 359, 380, 394, 418, 436, 472]
    
    x = np.linspace(50, 180, 1000)
    
    #This years top
    r = requests.get("http://www.iwf.net/results/ranking-list/?ranking_year=2015&ranking_agegroup=Senior&ranking_gender=M&ranking_category=all&ranking_lifter=all&x=18&y=10")
    soup = BeautifulSoup(r.content)
    rows = soup.find_all("tr")
    webbw = []
    for row in rows:
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            if i == 4:
                webbw.append(cell.text.strip())
            
    webtotal = []
    for row in rows:
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            if i == 7:
                webtotal.append(cell.text.strip())        
    
    
    p = figure(plot_width=500, plot_height=500)
    p.circle(bw, total, size=10, legend= "World Record")
    p.circle(webbw, webtotal, size=5, color = "red", legend="Others")
    
    p.line(x, approx(x), line_color="#D95B43", line_width=3, alpha=0.7, legend="Nel-Sinclair")
    
    p.title = "Body Weight vs Total"
    p.xaxis.axis_label="Body Weight in Kilos"
    p.yaxis.axis_label="Total in Kilos"
    p.legend.orientation = "bottom_right"
    
    p.xgrid.grid_line_color = None
    
    
    #If page empty return graph
    if request.method == 'GET': 
        script, div = components(p)
        html = render_template(
            'nsc.html',
            NS=1, ts=1,
            plot_script=script, plot_div=div 
        )
        return encode_utf8(html) 
        
    #else add point of user    
    else:
        app.vars['userbw'] = request.form['userbw']
        app.vars['usertotal'] = request.form['usertotal']
            #your performance
            
            
        if app.vars['userbw'] == '' or app.vars['usertotal'] == '':
            script, div = components(p)
            html = render_template(
                'nsc.html',
                NS=1, ts=1,
                plot_script=script, plot_div=div 
            )
            return encode_utf8(html) 
    
        else:
            userbw = float(app.vars['userbw'])
            usertotal = float(app.vars['usertotal'])
    
            #your sinclair
            m = 0.794358141
            n = 174.393
    
            ts = 0
            if userbw > n:
                ts = usertotal
        
            else:
                s = math.log(userbw/n, 10)
                ts = round(usertotal*(10**(m*(s**2))), 2)
        
            NS = round(-approx(userbw)+usertotal, 2)
            
            p.circle(userbw, usertotal, size=10, color = "green", legend="You")
            script, div = components(p)
            html = render_template(
                'nsc.html',
                NS=NS, ts=ts,
                plot_script=script, plot_div=div 
            )
            return encode_utf8(html)
        
    
        
        
############################################################################        
#World Records Page    
############################################################################
@app.route('/worldrecords', methods=['GET', 'POST'])
def WR():
    records56total = records[(records['Event Code']==3) & (records['Weight Class']==56)]
    palette = ["#053061", "#2126ac", "#4353c3", "#92c7de", "#d1e5f0",
           "#f7f1c7", "#fddbc7", "#f4a582", "#d6104d", "#b2182b", "#67e01f",
          "#023061", "#2162ac", "#4392c3", "#92c2de", "#a1e2f0",
           "#f3a7f7", "#fddbc3", "#f4a523", "#d6603a", "#b3182b", "#370d1f",
          "#053061", "#2166ac", "#4393c3", "#92c5de", "#d1e5f0",
           "#f4f7f4", "#fdd3c7", "#f4a512", "#d2344d", "#b2382a", "#61001f"]

    colormap = {}
    k = 0
    for lifter in records56total['Lifter']:
        if lifter not in colormap:
            k = k+1
            colormap[lifter]=k

    colors = [colormap[x] for x in records56total['Lifter']]


    melting_colors = [palette[i] for i in colors]

    

    p = figure(plot_width=650, plot_height=400)

    p.title = "56kg Class Total World Records Over Time."

    p.xaxis.axis_label="Year"
    p.yaxis.axis_label="Total"
    p.grid.grid_line_color="white"

    p.circle(records56total['Year'], records56total['Record'], size=12,
             color=melting_colors, line_color="black", fill_alpha=0.8)

    p.text(records56total['Year']+2, records56total['Record'],
           text=records56total['Lifter'],text_color="#333333",
           text_align="center", text_font_size="7pt")
    
    if request.method == 'GET':
        script, div = components(p)
        html = render_template(
            'worldrecords.html',
            plot_script=script, plot_div=div 
        )
        return encode_utf8(html)
    
    else: 
        app.vars['event'] = request.form['event']
        app.vars['group'] = request.form['group']

        event = int(app.vars['event'])
        group = int(app.vars['group'])   
            
        records_disp = records[(records['Event Code']==event) & (records['Weight Class']==group)]
        palette = ["#053061", "#2126ac", "#4353c3", "#92c7de", "#d1e5f0",
               "#f7f1c7", "#fddbc7", "#f4a582", "#d6104d", "#b2182b", "#67e01f",
                "#023061", "#2162ac", "#4392c3", "#92c2de", "#a1e2f0",
                   "#f3a7f7", "#fddbc3", "#f4a523", "#d6603a", "#b3182b", "#370d1f",
                   "#053061", "#2166ac", "#4393c3", "#92c5de", "#d1e5f0",
                   "#f4f7f4", "#fdd3c7", "#f4a512", "#d2344d", "#b2382a", "#61001f"]

        colormap = {}
        k = 0
        for lifter in records_disp['Lifter']:
            if lifter not in colormap:
                k = k+1
            colormap[lifter]=k

        colors = [colormap[x] for x in records_disp['Lifter']]

        melting_colors = [palette[i] for i in colors]

        p = figure(plot_width=650, plot_height=400)
        
        if group == 116:
            group_disp = '105+'
        else:
            group_disp = group
                
        if event == 1:
            event_disp = 'Snatch'
        elif event == 2:
            event_disp = 'C and J'
        elif event ==3: 
            event_disp = 'Total'
        elif event == 4:
            event_disp = 'Press'
            
        
        title = '%s%s %s %s %s' % (group_disp,'kg', 'Class', event_disp,'World Records Over Time.')
        p.title = title

        p.xaxis.axis_label="Year"
        p.yaxis.axis_label=event_disp
        p.grid.grid_line_color="white"

        p.circle(records_disp['Year'], records_disp['Record'], size=12,
                 color=melting_colors, line_color="black", fill_alpha=0.8)

        p.text(records_disp['Year']+2, records_disp['Record'],
               text=records_disp['Lifter'],text_color="#333333",
               text_align="center", text_font_size="7pt")            

        script, div = components(p)
        html = render_template(
            'worldrecords.html',
            plot_script=script, plot_div=div 
        )
        return encode_utf8(html)



############################################################################
#Projections
############################################################################
@app.route('/projections', methods=['GET', 'POST'])
def P():
    if request.method == 'GET': 
        html = render_template(
            'projections.html',
            total_disp=1, NS_disp=1,
        )
        return encode_utf8(html)
    else:
        app.vars['agep'] = request.form['agep']
        app.vars['bwp'] = request.form['bwp']
        app.vars['totalp'] = request.form['totalp']
        
        if app.vars['agep'] == 'Ruben Olmedo':
            html = render_template(
                'projections.html',
                total_disp='A new WR of 305.5', NS_disp='OVER 9000!!!!',
            )
            return encode_utf8(html)   
        
        else:
            if app.vars['agep']== '' or app.vars['bwp'] == '' or app.vars['totalp']== '':
                html = render_template(
                    'projections.html',
                    total_disp=1, NS_disp=1,
                )
                return encode_utf8(html)
                
                
            else:    
            
                agep = float(app.vars['agep'])
                bwp = float(app.vars['bwp'])
                totalp = float(app.vars['totalp'])
        
        
        
                #NSp = round(-approx(bwp)+totalp, 2)
                #for index, row in recent_data.iterrows():
                    #if abs(row['Age']-agep)<=2 and abs(row['NSC']-NSp)<=2:
                        #comparison = (row['LC'],row['CC'],row['Birth'],row['Year'],row['Year']+1)
                comparison = (5933, 15, 2016-agep, agep,2016)        
                NSp2 = nei_model_pred.predict(comparison)   
                NSp = round(-approx(bwp)+totalp, 2)
                
               
                total_disp = NSp-NSp2+totalp
            
                
                html = render_template(
                    'projections.html',
                    total_disp=total_disp, NS_disp=NSp2,
                )
                return encode_utf8(html)    
                


############################################################################
#Countries Page
############################################################################
@app.route('/countries')
def C():
    return render_template('countries.html')
            
            
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 