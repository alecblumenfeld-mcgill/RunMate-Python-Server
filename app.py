"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""

import os
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.cors import CORS, cross_origin

import logging
from User import User, AuthenticatedUser
from Run import Run
from Goal import Goal

app = Flask(__name__)
cors = CORS(app, resources={r"/routines": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')



@app.route('/routines/<userId>')
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def routines(userId):
    thisUser = User(userId=userId)
<<<<<<< .merge_file_SnE6Vd
=======
    #print(thisUser)
>>>>>>> .merge_file_l2k8I4
    return thisUser.getRoutines()


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/buddies/<userId>')
def buddies(userId):
    thisAuthUser = AuthenticatedUser(userId)
    return thisAuthUser.getFriendSuggestions()



@app.route('/checkTrophies' , methods=['GET'])
def checkTrophies():
    userId = request.args.get('userId')
    runId = request.args.get('runId')
    thisRunner = AuthenticatedUser(userId)
    thisRun = Run(thisRunner.sessionToken, runId)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
