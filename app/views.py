
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


@app.route('/')
@app.route('/input')
def diy_input():
    return render_template("input_before_changes.html")
  
#@app.route('/output')
#def cities_output():
#    return render_template("output.html")

@app.route('/output')
def diy_output():
    #pull 'ID' from input field and store it
    projectID = request.args.get('ID')
    db = mdb.connect(user="root", host="localhost", db="instructables",  charset='utf8', unix_socket='/tmp/mysql.sock', port='3307')
   
    pID = "/id/" + urlExtract(projectID) + "/"
    print "the current url is: " + pID
    with db:
        cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
        cur.execute("SELECT  title, complexEstimate, id, imgURL FROM techFeatures WHERE url ='%s';" %pID )
        query_results = cur.fetchall()
        chosen = []
        for result in query_results:
            chosen.append(dict(title = result[0], complexity = result[1], rowNum = result[2], imgURL = result[3]) )
        if not chosen:
            db.close()
            return render_template("404.html", ID = "Invalid project, not all projects have the proper format unfortunately. :(")
        
        # Now get from the "similars" table the 15 closest from our chosen row
        cur.execute("SELECT * FROM similars WHERE X = %s;", chosen[0]["rowNum"])  
        indices15 = cur.fetchall()
        
        indices15 = [el +1 for el in indices15[0]]  # NEED TO GIVE techFeatures id+1 to get proper project      
        #for ind in indices15[0][1:]:
            
        format_string = ','.join(['%s'] * len(indices15))
        cur.execute("SELECT  title, complexEstimate, url, imgURL FROM techFeatures WHERE id IN (%s) ORDER BY FIELD (id,%s);" %(format_string,format_string), tuple(indices15+indices15) )
        query_results = cur.fetchall()
    
    closests = []
    for result in query_results:
        closests.append(dict(projectTitle = result[0], 
                             compEst = result[1], 
                             url = "http://www.instructables.com" + str(result[2]),
                             imgURL = "http://cdn.instructables.com" + str(result[3]) 
                             )
                        )
    
        
    cur_compl = chosen[0]["complexity"]
    simplest = cur_compl #this is the level of simplest
    hardest = cur_compl
    same = cur_compl
    
    for p in closests:
        if abs(p["compEst"] - same) < 0.5:
            simP = p
            same = 9999
        elif p["compEst"] < simplest:
            simpleP = p
            simplest = p["compEst"]
        elif p["compEst"] > hardest:        
            hardP = p
            hardest = p["compEst"]
    if "hardP" not in locals():
        hardP = dict(projectTitle = "OUPS! No harder projects within most similar instructibles",  compEst = 0.000, 
                                     url = pID,
                                     imgURL = "/static/img/warning.jpg")
    if "simpleP" not in locals():
        simpleP = dict(projectTitle = "OUPS! No simpler projects within most similar instructibles",  compEst = 0.000, 
                                     url = pID,
                                     imgURL = "/static/img/warning.jpg")
    
    # This rounds the levels
    chosen[0]["complexity"] = round(chosen[0]["complexity"],1)
    simpleP["compEst"] = round( simpleP["compEst"], 1 )
    simP["compEst"] = round( simP["compEst"], 1 )
    hardP["compEst"] = round( hardP["compEst"], 1 )
    
    
    return render_template("output.html", chosen = chosen[0], pID = pID, simpleP = simpleP, simP = simP, hardP = hardP)








@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
  
  