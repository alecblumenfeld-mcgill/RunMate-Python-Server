"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

"""

import os
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.cors import CORS, cross_origin

import logging
from config import *
from User import User, AuthenticatedUser
from Run import Run
from Goal import Goal

app = Flask(__name__)

CORS(app)


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')



@app.route('/routines/<userId>')
def routines(userId):
    try:
        thisUser = User(userId=userId)
        if thisUser == None :
            return jsonify(error="User not found")
        return thisUser.getRoutines()
    except :
        raise
    

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/buddies/<userId>')
def buddies(userId):

    try :
        thisAuthUser = AuthenticatedUser(userId)
        if thisAuthUser == None:
            return jsonify(error="User not found")
        return thisAuthUser.getFriendSuggestions()
    except :
        return jsonify(error="None of your facebook friends have downloaded RunMate!")


@app.route('/checkTrophies' , methods=['GET'])
def checkTrophies():
    try :
        userId = request.args.get('userId')
        runId = request.args.get('runId')
        thisRunner = AuthenticatedUser(userId)
        if thisRunner == None :
            return jsonify(error="User not found")
        thisRun = Run(thisRunner.sessionToken, runId)
        return thisRun.getTrophies()
    except :
        return jsonify(error="No goals completed")

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

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))

if __name__ == '__main__':
    app.run(debug=True)
