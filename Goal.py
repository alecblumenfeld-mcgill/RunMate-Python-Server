from config import *

class Goal :

	def __init__(self, trophyId) :
		
		try :
			connection.request('GET', '/1/classes/TrophyInformation/%s' % trophyId, '', {
		       "X-Parse-Application-Id": os.environ["RUNMATE_CONST_APPID"],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			result = json.loads(connection.getresponse().read().decode('utf-8'))
		except http.client.RemoteDisconnected :
			connection.request('GET', '/1/classes/TrophyInformation/%s' % trophyId, '', {
		       "X-Parse-Application-Id": os.environ["RUNMATE_CONST_APPID"],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			result = json.loads(connection.getresponse().read().decode('utf-8'))
		except :
			restartConnection()
			connection.request('GET', '/1/classes/TrophyInformation/%s' % trophyId, '', {
		       "X-Parse-Application-Id": os.environ["RUNMATE_CONST_APPID"],
		       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY']
		     })
			result = json.loads(connection.getresponse().read().decode('utf-8'))

		if not result :
			return jsonify(error="Goal not found")

		self.distance = result['distance']

		if 'minutes' in result :
			self.time = result['minutes']*60
			# Timedeltas only give us values in seconds so better to have this as seconds for comparison
		else :
			self.time = 0

		self.completed = result['completed']

		self.objectId = result['objectId']

		self.userId = result['userObjectID']

	def setCompleted (self) :

		# Set user 
		try :
			connection.request('PUT', '/1/classes/TrophyInformation/%s' % self.objectId, json.dumps({
			       "completed": True
			     }), {
			       "X-Parse-Application-Id": os.environ["RUNMATE_CONST_APPID"],
			       "X-Parse-REST-API-Key": os.environ['RUNMATE_CONST_APIKEY'],
			       "Content-Type": "application/json"
			     })
			result = json.loads(connection.getresponse().read().decode('utf-8'))
		except http.client.RemoteDisconnected :
			return self.setCompleted()
		except :
			restartConnection()
			return self.setCompleted()

		if 'updatedAt' in result :
			return self.objectId
		else :
			return None
