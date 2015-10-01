
  # [done] get index of chosen URL
  # [done] get the complexity from that url 
  # [dont need if I don't recompute model] get 9 features from that url
  # Load tfidf weights
#####Maybe I will only need to compute the cosine similarity top 30 indices...and then I can have it sorted
  # compute cosine similarity with the other database of features
  # yield top 100 projects
  # get url, title, complexity from MySQL
  # find highest words of interest from  
  # scrape the website to display image.
  
  # will need urllib2 or
  ################################
  
  
from flask import render_template
from flask import request
from numpy import round
import pickle as pkl

import pymysql as mdb
#import MySQLdb

from app import app

from a_Model import urlExtract
from a_Model import getSimProjects

@app.route('/')
@app.route('/input')
def diy_input():
    
    return render_template("input.html")
  
#@app.route('/output')
#def cities_output():
#    return render_template("output.html")

@app.route('/output')
def diy_output():
    #pull 'ID' from input field and store it
    projectID = request.args.get('ID')
    db = mdb.connect(user="root", host="localhost", db="instructables",  charset='utf8', unix_socket='/tmp/mysql.sock', port='3307')
   
    url = "/id/" + urlExtract(projectID) + "/"
    print "the current url is: " + url
    with db:
        cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
        cur.execute("SELECT  title, complexEstimate, id FROM technoFEATURES WHERE url ='%s';" %url )
        query_results = cur.fetchall()

    chosen = []
    for result in query_results:
        chosen.append(dict(title = result[0], complexity = result[1], rowNum = result[2]) )
  
    if not chosen:
        return render_template("404.html", ID = "Invalid project, not all projects have the proper format unfortunately. :(")
    
    # get the indices
    #indices15 = getSimProjects(chosen[0]["rowNum"]):
    if 'bmatch' not in locals():
        with open("../Data/matchlist.pickle", 'rb') as f:
            bestmatch = pkl.load(f)
    indices15 = bestmatch[chosen[0]["rowNum"]]
    
    closests = []
    with db:
        cur = db.cursor()
        # ignore first
        for ind in indices15[1:]:
            cur.execute("SELECT  title, complexEstimate, url FROM technoFEATURES WHERE id ='%d';" %(ind+1) )
            query_results = cur.fetchall()
            for result in query_results:
                closests.append(dict(projectTitle = result[0], 
                                     compEst = result[1], 
                                     url = "www.instructables.com/id/" + str(result[2]) + "/")
                               )
        
 #### add index + 1 from python to "id" of the SQL
    cur_compl = chosen[0]["complexity"]
    simplest = cur_compl #this is the level of simplest
    hardest = cur_compl
    same = cur_compl
    for p in closests:
        if p["compEst"] < simplest-1:
            simplest = 0
            simpleP = p
        elif p["compEst"] > hardest+1:        
            hardest = 6
            hardP = p
        elif abs(p["compEst"] - same) < 0.5:
            simP = p #we found a similar project
            same = 1000
    
    # This rounds the levels
    chosen[0]["complexity"] = round(chosen[0]["complexity"])
    simpleP["compEst"] = round( hardP["compEst"], 1 )
    simP["compEst"] = round( simP["compEst"], 1 )
    hardP["compEst"] = round( simpleP["compEst"], 1 )
    
    return render_template("output.html", chosen = chosen[0], simpleP = simpleP, simP = simP, hardP = hardP)








@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
  
  