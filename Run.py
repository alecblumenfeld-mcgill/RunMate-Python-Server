from config import *


    
class Run :

	def __init__(self, sessionToken, runId) :
		
		params = urllib.parse.urlencode({"where":json.dumps({
			"objectId" : runId
		})})
		try :
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": "dX9JzxUVmJXzIqKh3keU7GCHTRwzqqp3dmI9TuRu",
	   		  "X-Parse-REST-API-Key": "0N1cPT6n8yz4dLegykA0D93EKToELIKrtyjKeRPX",
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except http.client.RemoteDisconnected :
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": "dX9JzxUVmJXzIqKh3keU7GCHTRwzqqp3dmI9TuRu",
	   		  "X-Parse-REST-API-Key": "0N1cPT6n8yz4dLegykA0D93EKToELIKrtyjKeRPX",
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except :
			restartConnection()
			connection.request('GET', '/1/classes/Run?%s' % params, '', {
	     	  "X-Parse-Application-Id": "dX9JzxUVmJXzIqKh3keU7GCHTRwzqqp3dmI9TuRu",
	   		  "X-Parse-REST-API-Key": "0N1cPT6n8yz4dLegykA0D93EKToELIKrtyjKeRPX",
	   		  "X-Parse-Session-Token" : str(sessionToken)
	   		 })
			result = json.loads(connection.getresponse().read().decode('utf-8'))['results']

		if result :
			run = result[0]
		else :
			self.error = True
			return None # Error : Run not found

		self.error = False

		self.distance = run['distance']
		self.userId = run['user']
		# self.userId = str(run['ACL'])[2:11])
		self.runId = runId
		self.runLocations = run['runlocations']

	def getTrophies(self) :

		if self.error == True :
			return None # Error: Run not found

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
			self.checkTrophy(goal)

	def checkTrophy(self, goal) :

		locList = []
		
		if goal.distance > self.distance :
			return False
		elif ((goal.distance <= self.distance) & (goal.time == 0)) :
			goal.setCompleted()
		else :
			return False # working on this
			for loc in self.runLocations :
				params = urllib.parse.urlencode({"where":json.dumps({
					"objectId" : loc
				})})
				connection.request('GET', '/1/classes/RunLocation?%s' % params, '', {
			       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
			       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
			     })
				runLoc = json.loads(connection.getresponse().read().decode('utf-8'))['results'][0]
				locList.append([runLoc['distance']*0.00062137, datetime.datetime.fromtimestamp(runLoc['timestamp']).strftime('%Y-%m-%d %H:%M:%S')])
			locList = sorted(locList, key=itemgetter(0))
			print(locList)


