from config import *
from Goal import Goal

class Run :

	def __init__(self, sessionToken, runId) :

		distanceList = []
		
		params = urllib.parse.urlencode({"where":json.dumps({
			"objectId" : runId
		})})
		try :
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
	   		  "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except http.client.RemoteDisconnected :
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
	   		  "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except :
			restartConnection()
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
	   		  "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']

		if result :
			run = result[0]
		else :
			self.error = True
			return jsonify(error="Run not found")

		self.error = False

		self.distance = run['distance']
		self.userId = run['user']
		self.runId = runId
		self.runLocations = run['runlocations']
		self.runData = self.pullRunLocations()
		if self.runData :
			for l in self.runData :
				distanceList.append(l[0])
			self.runDistances = distanceList

	def pullRunLocations(self) :

		locList = []
		
		try :
			params = urllib.parse.urlencode({"where":json.dumps({
				"objectId": {
					"$in" : self.runLocations
				}
			})})
			connection.request('GET', '/1/classes/RunLocation?%s' % params, '', {
		       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			results = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except ValueError:
			print("ValueError")
			return jsonify(error="RunLocs missing for run")

		for runLoc in results :
			locList.append([runLoc['distance']*0.00062137, datetime.datetime.fromtimestamp(runLoc['timestamp'])])

		locList = sorted(locList, key=itemgetter(0))
		return locList

	def getTrophies(self) :

		if self.error == True :
			return jsonify(error="Run not found")

		# Retrieve all uncompleted user goals
		params = urllib.parse.urlencode({"where":json.dumps({
			"completed" : False,
			"userObjectID" : self.userId
		})})
		try :
			connection.request('GET', '/1/classes/TrophyInformation?%s' % params, '', {
		       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			trophyList = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except http.client.RemoteDisconnected :
			return self.getTrophies()

		# Filter goals that shouldn't be considered
		for t in trophyList :
			goal = Goal(str(t['objectId']))
			if self.checkTrophy(goal) :
				#print("woohoo")
				return goal.setCompleted()
		return jsonify("No goals completed")

	def findNearest(self, array, value):
	    idx = (np.abs(array-value)).argmin()
	    return array[idx]

	def checkTrophy(self, goal) :

		locList = []
		
		if goal.distance > self.distance :
			return False
		elif ((goal.distance <= self.distance) & (goal.time == 0)) :
			return True
		else :
			if self.runData == None :
				return False
			else :
				loops = goal.distance / self.distance
				l = np.arange(0.0, loops, .1)
				for i in l :
					startMile = i
					#print ("startMile = %s" % startMile)
					endMile = i + goal.distance
					#print ("endMile = %s" % endMile)
					startInfo = self.findNearest(self.runDistances, startMile)
					#print("startInfo = %s" % startInfo)
					endInfo = self.findNearest(self.runDistances, endMile)
					#print("endInfo = %s" % endInfo)
					for d in self.runData :
						if (d[0] == startInfo) :
							startInfo = d
							print(d)
						if (d[0] == endInfo) :
							endInfo = d
							print(d)
					diffTime = endInfo[1] - startInfo[1]
					#print(diffTime)
					#print(goal.time)
					if diffTime.seconds == goal.time :
						#print("yes")
						return True
				return False
