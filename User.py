from config import *

class User:

	def __init__(self, **args) :

		self.error = False 
		if 'userId' in args:
			user = self.connection(args['userId'])
			if not user :
				self.error = True
		else :
			params = urllib.parse.urlencode({"where":json.dumps({ 
					args['param1']: args['param2']
				})})
			tempUser = self.paramConnection("User", params)['results']
			if tempUser :
				self.error = False
				user = tempUser[0]
			else :
				self.error = True
				user = []

		if 'runNum' in user :
			# User has not gone on any runs
			self.runNum = int(user['runNum'])
		else :
			# User has not gone on any runs
			self.runNum = 0

		if 'weight' in user :
			self.weight = float(user['weight'])
		else :
			self.weight = 0

		if 'goalWeight' in user :
			self.goalWeight = float(user['goalWeight'])
		else :
			self.goalWeight = 0

		if 'goalWeeks' in user :
			self.goalWeeks = float(user['goalWeeks'])
		else :
			self.goalWeeks = 0

		if 'authData' in user :
			self.accessToken = user['authData']['facebook']['access_token']
		else :
			self.accessToken = None

		if 'name' in user :
			self.name = user['name']

		if 'objectId' in user :
			self.userId = user['objectId']
		else :
			self.userId = 0

		if 'code' in user :
			return None
		
		if self.runNum != 0 :
			self.avgDistance = self.getTotalDistance()
			self.avgDistance = self.avgDistance/self.runNum
		else :
			self.avgDistance = 0
			
		if self.runNum != 0 :
			self.avgDistance = self.getTotalDistance()
			self.avgDistance = self.avgDistance/self.runNum
		else :
			self.avgDistance = 0

		self.totalDistance = self.getTotalDistance()

	def connection(self, userId) :
		try :
			connection.request('GET', '/1/users/%s' % userId, '', {
		       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			return json.loads(connection.getresponse().read().decode('utf-8'))
		except http.client.RemoteDisconnected :
			return self.connection(userId)
		except :
			restartConnection()
			return self.connection(userId)

	def paramConnection(self, cl, params) :

		if cl == "User" :
			try :
				connection.request('GET', '/1/users?%s' % params, '', {
			       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
			       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
			     })
				return json.loads(connection.getresponse().read().decode('utf-8'))
			except http.client.RemoteDisconnected :
				return self.paramConnection("User", params)
			except :
				restartConnection()
				return self.paramConnection("User", params)
		else :
			try :
				connection.request('GET', '/1/classes/%s?%s' % (cl, params), '', {
			       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
			       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
			     })
				return json.loads(connection.getresponse().read().decode('utf-8'))
			except http.client.RemoteDisconnected :
				return self.paramConnection(cl, params)
			except :
				restartConnection()
				return self.paramConnection(cl, params)

	def getTotalDistance(self) :

		if self.runNum == 0 :
			return 0

		params = urllib.parse.urlencode({"where":json.dumps({ 
					'userObjId': self.userId
				})}, {"order":"-timestamp"})

		res = self.paramConnection("RunLocation", params)['results']

		currentRun = 0
		sumRuns = 0
		for item in res :
			if item['userObjId'] == self.userId :
				if item['runHash'] != currentRun :
					sumRuns = sumRuns+(item['distance']*0.00062137) # Currently recording in meters
					currentRun = item['runHash']
		totalDist = sumRuns

		return totalDist

	def subsetSum(self, maxNum, i, possibleRoutines, numbers, target, partial=[]) :

		# Find possible routines for weight loss assuming certain caloric goal per week
		s = sum(partial)
		partialTemp = np.array(partial)
		partialNew = np.rint(partialTemp/(.63*self.weight))

		if ((s == target) | ((s > target-75) & (s < target+75))) :
			if len(partialNew) < 8 : # Throw out routines entailing more than one run a day
				possibleRoutines.append(partialNew.tolist())
		if s >= target :
		    return
		for i in range(len(numbers)) :
			# Return all possible mileage options per week, we will only display 3 options for the user
			if i == maxNum :
				return possibleRoutines
			n = numbers[i]
			remaining = numbers[i+1:]
			self.subsetSum(maxNum, i, possibleRoutines, remaining, target, partial + [n])

	def getAllRoutines(self) :

		if self.goalWeight>self.weight :
			jsonify(error="Goal weight higher than current weight")

		if self.avgDistance == 0 :
			avgDist = 4 # Default value for run variations
		else :
			avgDist = self.avgDistance

		avgDist = 4 # Testing

		# Calories burnt per mile: .63 * weight (lbs)
		multNum = .63*self.weight

		# 3500 calorie deficit to lose 1 pound
		perWeek = (self.weight-self.goalWeight)/self.goalWeeks

		# Goal lbs to lose per week multiplied by calorie deficit needed
		defPerWeek = perWeek * 3500
		numbers = [(avgDist-3)*multNum, (avgDist-2)*multNum, (avgDist-1)*multNum, avgDist*multNum, (avgDist+1)*multNum, (avgDist+2)*multNum, (avgDist-2)*multNum, (avgDist-1)*multNum, avgDist*multNum, (avgDist+1)*multNum, (avgDist+2)*multNum]
		
		# TODO Add logic for recommended mileage rather than variation on average
		return self.subsetSum(len(numbers)-1, 0, [], numbers, defPerWeek)

	def getRoutines(self) :

		routines = self.getAllRoutines()

		if routines == None :
			return jsonify(error="Unable to calculate routines, please allot more time to reach your goal weight")

		suggestions = []
		# Remove duplicates
		i = -1
		for r in routines :
			i = i+1
			r.sort()
			if (i != routines.index(r)) :
				routines.remove(r)

		# Suggestion options for different numbers of workout days a week
		for i in range(7) :
			for r in routines :
				if len(r) == i :
					suggestions.append(r)
					break

		if suggestions == [] :
			return jsonify(error="Unable to calculate routines, please allot more time to reach your goal weight")
		else :
			return jsonify(routines=suggestions)
class AuthenticatedUser(User) :

	def __init__(self, userId) :
		User.__init__(self, userId = userId)
		self.sessionToken = self.getSessionToken(userId)

	def getSessionToken(self, userId) :
		params = urllib.parse.urlencode({"where":json.dumps({ 
				"user":{
			        "__type": "Pointer",
			        "className": "_User",
			        "objectId": userId
			    }
			})})
		try :
			connection.request('GET', '/1/sessions/?%s' % params, '', {
		       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
		       "X-Parse-Master-Key": os.environ['RUNMATE_CONST_MASTKEY']
		     })
			session = json.loads(connection.getresponse().read().decode('utf-8'))['results']
		except http.client.RemoteDisconnected :
			return self.getSessionToken(userId)
		except :
			restartConnection()
			return self.getSessionToken(userId)

		for s in session :
			sessionToken = s['sessionToken']
			break

		return sessionToken

	def connection(self, userId) :
		
		try :
			connection.request('GET', '/1/users/%s' % userId, '', {
		       "X-Parse-Application-Id": os.environ['RUNMATE_CONST_APPID'],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
		       "X-Parse-Session-Token" : str(self.getSessionToken(userId))
		     })
			return json.loads(connection.getresponse().read().decode('utf-8'))
		except http.client.RemoteDisconnected :
			return self.connection(userId)
		except :
			restartConnection()
			return self.connection(userId)

	def serializeFriendObject(self, friend) :
		return {
            'user_name': friend[0],
            'avg_distance': np.around(friend[1], decimals = 2),
            'total_distance': np.around(friend[2], decimals = 2),
            'object_id' : friend[3]
            }

	def getFbFriends(self) :

		graph = facebook.GraphAPI(self.accessToken)
		profile = graph.get_object("me")
		return graph.get_connections("me", "friends")

	def getFriendSuggestions(self) :

		friends = self.getFbFriends()
		noneList = []
		avgList = []
		suggestions = []

		try :
			for f in friends['data'] :
				fId = f['id']

				friend = User(param1="facebookIdPublic", param2=str(fId))
				
				if friend.userId != 0 :
					if friend.avgDistance == 0 :
						noneList.append(friend.name)
					else :
						avgList.append([friend.name, friend.avgDistance, friend.avgDistance, friend.totalDistance, friend.userId])
		except KeyError:
			return jsonify(error="No friends found")

		if (len(avgList) == 0) & (len(noneList)==0) :
			suggestions = []
		elif (len(avgList) == 0) & (len(noneList)<=3) :
			for i in noneList :
				suggestions.append([i[0], i[2], i[3], i[4]])
		elif (len(avgList) == 0) & (len(noneList)) >3 :
			for i in noneList[:3] :
				suggestions.append([i[0], i[2], i[3], i[4]])
		elif len(avgList) <= 3 :
			for val in avgList :
				suggestions.append([val[0], val[2], val[3], val[4]])
		else :
			if self.avgDistance == 0 :
				# Just return the three first people in the list
				for val in avgList[:3] :
					suggestions.append([val[0], val[2], val[3], val[4]])
			else :
				for val in avgList :
					val[1] = abs(val[1]-self.avgDistance) 

				# New format: user and distance from userId's averageDistance
				# Return the users with closest average distances to the user in question
				avgList = sorted(avgList, key=itemgetter(1))
				for val in avgList[:3] :
					suggestions.append([val[0], val[2], val[3], val[4]])

		if suggestions == [] :
			return jsonify(error="No friends found")
		else :
			return jsonify(user=[self.serializeFriendObject(x) for x in suggestions])
		return jsonify(error="No friends found")
