import os
from flask import Flask, jsonify, request
import soundcloud
import logging
import Queue
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from string import Template
import time

from emailSegments import emailSegments
from emailSensitives import emailSensitives

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = False

MAX_TRIES=10
SLEEP_TIME=1

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')
    

def makeHTMLPathSection(resultData, whichPath, isLastSection, colorCode):
	datalength= len(resultData.get("data")[whichPath])
	NewHtmlPathSectionTop=Template(emailSegments.htmlPathSectionTop).safe_substitute(colorCode=colorCode, user=str(resultData.get("data")[whichPath][-1].get("username")), followers_count=resultData.get("data")[whichPath][-1].get("followers_count"))
	htmlArtistsAndArrows=""" """
	personCounter=0
	for person in resultData.get("data")[whichPath]:
		newHtmlAvatar=Template(emailSegments.htmlInsertAvatar).safe_substitute(permaLinkUrl=str(person.get("permalink_url")), picURL=str(person.get("avatar_url")))
		htmlArtistsAndArrows=htmlArtistsAndArrows+newHtmlAvatar
		if(personCounter!=datalength-1):
			htmlArtistsAndArrows=htmlArtistsAndArrows+ emailSegments.htmlInsertArrow

		personCounter=personCounter+1
	if(isLastSection==True):
		return	NewHtmlPathSectionTop+htmlArtistsAndArrows+emailSegments.htmlPathSectionBottomButton
	else:
		return	NewHtmlPathSectionTop+htmlArtistsAndArrows+emailSegments.htmlPathSectionBottomNoButton




def makeEmailtarget(resultData):
	logger.info("MAKING TARGET EMAIL")
	datalength= len(resultData.get("data")[0])	
	topTitle= "You're {} degree(s) away from {}!".format(str(datalength-1), str(resultData.get("username")))
	NewTopTitle=Template(emailSegments.htmlTOP).safe_substitute(topTitle=topTitle)

	pathsection=makeHTMLPathSection(resultData,0, True, "#e67e22")

	return NewTopTitle+pathsection+emailSegments.htmlBottom



def makeEmailMax(resultData):
	logger.info("MAKING MAX EMAIL")
	numPaths=len(resultData.get("data"))
	if(resultData.get("username") is None):
		topTitle= "Here are the paths to the top 3 most popular users within your network within {} degree(s)!".format(str(resultData.get("degree")))
	else:
		topTitle="We couldn't find a path between you and {} within {} degrees, but here are the paths to the top 3 most popular users within your network within {} degrees!".format(str(resultData.get("username")), str(resultData.get("degree")), str(resultData.get("degree")))
	
	colors=["#e67e22","#eb9950", "#f0b47e"]	

	NewTopTitle=Template(emailSegments.htmlTOP).safe_substitute(topTitle=topTitle)

	pathsSections=""" """
	pathCount=0
	for paths in resultData.get("data"):
	

		if(pathCount!=numPaths-1):
			sec=makeHTMLPathSection(resultData, pathCount,False, colors[pathCount])
		else:
			sec=makeHTMLPathSection(resultData, pathCount,True, colors[pathCount])	
	

		pathsSections=pathsSections+sec
		pathCount=pathCount+1


	return NewTopTitle+pathsSections+emailSegments.htmlBottom		

	

def makeEmailFail():
	logger.info("MAKING FAIL EMAIL")
	NewTopTitle=Template(emailSegments.htmlTOP).safe_substitute(topTitle="Sorry, soundcloud seems to be down. We're sorry, please try again!")

	NewEmptyPathSec=Template(emailSegments.htmlPathSectionTopNoPath).safe_substitute(colorCode="#e67e22")

	return NewTopTitle+NewEmptyPathSec+emailSegments.htmlPathSectionBottomButton+emailSegments.htmlBottom



def emailPath(pathToMail, email):
	me = emailSensitives.address
	you = email

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Your Results!"
	msg['From'] = formataddr((str(Header('Degrees Of Sound', 'utf-8')), me))
	#msg['From'] = me
	msg['To'] = you

	# Create the body of the message (a plain-text and an HTML version).
	text = "degrees of sound results email"		#pathToMail
	
	html=""" """
	if(pathToMail is None):
		html=makeEmailFail()	
	elif(pathToMail.get("type")=="target"):
		html= makeEmailtarget(pathToMail)
	elif(pathToMail.get("type")=="max"):
		html= makeEmailMax(pathToMail)
	
	
	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)


	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(me, emailSensitives.pw)
		server.sendmail(me, you, msg.as_string())
		server.close()
		logger.info('successfully sent the mail')
	except:
		logger.info("email fail to send, probably doesn't exist")




def bfs(graph_to_search, start, end, degree):
    queue = [[start]]
    visited = set()

    while queue:
        # Gets the first path in the queue
		path = queue.pop(0)

		if len(path) - 1 > degree:
			return []
        
		# Gets the last node in the path
		vertex = path[-1]

        # Checks if we got to the end
		if vertex == end:
			return path
        # We check if the current node is already in the visited nodes set in order not to recheck it
		elif vertex not in visited:
			# enumerate all adjacent nodes, construct a new path and push it into the queue
			for current_neighbour in graph_to_search.get(vertex, []):
				new_path = list(path)
				new_path.append(current_neighbour)
				queue.append(new_path)

            # Mark the vertex as visited
			visited.add(vertex)


def getfollowersFromPerma(client, artistPerma, toEmail):
	#this has now been changed to give back both a user's permaLink but also their followers count
	pageSize=200
	result = []

	i=0
	while True:			
		try:
			artist=client.get('/resolve', url='http://soundcloud.com/'+ str(artistPerma))
			id=artist.id
			break
		except Exception as e:
			logger.info("something went wrong during resolve for "+artistPerma+", TRYING AGAIN")
			logger.info(e)
			if "404" in str(e):
				logger.info(artistPerma+ "no longer exists")
				return result #should be empty
			else:	
				i+=1
				time.sleep(SLEEP_TIME)
				if(i==MAX_TRIES):
					logger.info("Soundcloud seems to be down")
					emailPath(None, toEmail)
					return None
	i=0
	while True:
		try:
			followers=client.get("/users/"+str(id)+"/followers/", limit=pageSize, linked_partitioning=1)
			break
		except:
			logger.info("something went wrong during the followers for "+ artistPerma+" TRYING AGAIN")
			i+=1
			time.sleep(SLEEP_TIME)
			if(i==MAX_TRIES):
				logger.info("Soundcloud seems to be down")
				emailPath(None, toEmail)
				return None
				#followers=client.get("/users/"+str(id)+"/followers/", limit=pageSize, linked_partitioning=1)
				#sys.exit(0)

	nextPageURI=followers.next_href

	for artist in followers.collection:
		result.append({"permalink": artist.permalink, "followers_count": artist.followers_count})

	if nextPageURI is None:
		logger.info("Obtained "+str(len(result))+" followers for "+ artistPerma)
		return result			
	else:
		while nextPageURI is not None:
			i=0
			while True:
				try:
					nextfollowers=client.get(nextPageURI, limit=pageSize, linked_partitioning=1)
					break
				except:
					logger.info("something went wrong during the get next followers for "+ artistPerma+". The nextPageURI was "+str(nextPageURI)+ " TRYING AGAIN")
					i+=1
					time.sleep(SLEEP_TIME)
					if(i==MAX_TRIES):
						logger.info("Soundcloud seems to be down")
						emailPath(None, toEmail)
						return None
						#nextfollowers=client.get(nextPageURI, limit=pageSize, linked_partitioning=1)
			nextPageURI=nextfollowers.next_href
			for artist in nextfollowers.collection:
				result.append({"permalink": artist.permalink, "followers_count": artist.followers_count})	
		logger.info("Obtained "+str(len(result))+" followers for "+ artistPerma)
		return result	



def bfsSC(start, end, degree, client,toEmail):
	queue = [[start]]
	visited = set()
	currentDegree=0
	leafLevelComing=False

	#initial max values are negative because no one can have negative followers
	max=-1
	maxArtist=None
	maxPath=None

	max2=-2
	maxArtist2=None
	maxPath2=None

	max3=-3
	maxArtist3=None
	maxPath3=None
	

	while queue: #infinite loop because we are not dealing with a finite graph---soundcloud
    	# Gets the first path in the queue
		path = queue.pop(0)

		currentDegree=len(path)-1

		if(currentDegree==(int(degree))):
			leafLevelComing=True

		if currentDegree > int(degree):
			if maxArtist is not None:
				logger.info("max artist: "+maxArtist.get("permalink")+" who has "+ str(maxArtist.get("followers_count")) +" followers. printing max path")
			if maxArtist2 is not None:
				logger.info("max artist: "+maxArtist2.get("permalink")+" who has "+ str(maxArtist2.get("followers_count")) +" followers. printing max path")
			if maxArtist3 is not None:
				logger.info("max artist 3: "+maxArtist3.get("permalink")+" who has "+ str(maxArtist3.get("followers_count")) +" followers")

			return {'type': 'max', 'pathdata': [maxPath, maxPath2, maxPath3]}
			
        
		# Gets the last node in the path
		vertex = path[-1]

		# Checks if we got to the end
		if vertex == end:
			logger.info(str(maxPath))
			return {'type': 'target', 'pathdata': [path]}
			
		# We check if the current node is already in the visited nodes set in order not to recheck it
		elif vertex not in visited:
			# enumerate all adjacent nodes, construct a new path and push it into the queue
			results=getfollowersFromPerma(client,vertex,toEmail)

			if results is None:
				return results 

			if len(results)!=0:
				for current_neighbour in results:
					new_path = list(path)
					new_path.append(current_neighbour.get('permalink'))
					queue.append(new_path)
					
					if int(current_neighbour.get("followers_count"))>=max:

						max3=max2
						maxArtist3=maxArtist2
						maxPath3=maxPath2

						max2=max
						maxArtist2=maxArtist
						maxPath2=maxPath

						max=int(current_neighbour.get("followers_count"))
						maxArtist=current_neighbour
						maxPath=new_path	

					if current_neighbour.get('permalink')==end:
						logger.info(str(maxPath))
						return {'type': 'target', 'pathdata': [new_path]}
					
			if leafLevelComing==True:
				if maxArtist is not None:
					logger.info("max artist: "+maxArtist.get("permalink")+" who has "+ str(maxArtist.get("followers_count")) +" followers")
				if maxArtist2 is not None:	
					logger.info("max artist 2: "+maxArtist2.get("permalink")+" who has "+ str(maxArtist2.get("followers_count")) +" followers")
				if maxArtist3 is not None:	
					logger.info("max artist 3: "+maxArtist3.get("permalink")+" who has "+ str(maxArtist3.get("followers_count")) +" followers")
				return {'type': 'max', 'pathdata': [maxPath, maxPath2, maxPath3]}
				
				
			# Mark the vertex as visited
			visited.add(vertex)
		elif vertex in visited:
			logger.info(vertex+ "HAS ALREADY BEEN VISITED!")


			





@app.route('/api/entryPoint', methods=['POST'])
def extractInfo():
	toEmail=request.json.get('email')
	degreeReq=request.json.get('degree')
	clientID=request.json.get('clientID')
	artistPermaLink=request.json.get('artistPermaLink')
	artistUsername=None;
	currUserPermalink=request.json.get('currUserPermalink')
	client = soundcloud.Client(client_id=clientID)

	logger.info("Obtained client ID:"+str(clientID)+ " current artist permalink: "+str(currUserPermalink)+ " target artist permalink:"+str(artistPermaLink)+" degree request: "+str(degreeReq)+" email: "+str(toEmail))

	MODE=None
	if(artistPermaLink==""):
		MODE="max"	
	else:
		MODE="target"
				
	if(MODE=="target"):	



		i=0
		while True:
			try:#check to see if target artist even exists 
				artist=client.get('/resolve', url='http://soundcloud.com/'+ str(artistPermaLink))
				artistUsername=artist.username
				logger.info("artist EXISTS!!!!!!!")
				break		
			except Exception as e:
				if "404" in str(e):
					logger.info("artist entered doesn't exist'")
					return jsonify({"error": "404"})
				else:
					logger.info("something went wrong trying to do the artist existance resolve for "+ str(artistPermaLink))
					i += 1
					time.sleep(SLEEP_TIME)
					if(i == MAX_TRIES):
						logger.info("Soundcloud seems to be down")
						emailPath(None, toEmail)
						return jsonify({"error": "500"})

	

	results=bfsSC(currUserPermalink,artistPermaLink,degreeReq, client,toEmail)

	if results is None:
		return jsonify({"error": "500"})

	datapaths=[]
	for path in results.get('pathdata'):

		combinedProfiles=[]
		if(path is None):
			break
	

		for artist in path:
			i=0
			while True:				
				try:
					artist=client.get('/resolve', url='http://soundcloud.com/'+ str(artist))
					break
				except Exception as e:
					logger.info("something went wront trying to resolve"+ str(artist)+ "when creating results")
					logger.info(e)
					i += 1
					time.sleep(SLEEP_TIME)
					if(i == MAX_TRIES):
						logger.info("Soundcloud seems to be down")
						emailPath(None, toEmail)
						return jsonify({"error": "500"})
						#sys.exit(0)

			combinedProfiles.append({
				'first_name': artist.first_name,
				'last_name':  artist.last_name,
				'full_name': artist.full_name,
				'city': artist.city,
				'country': artist.country,
				'avatar_url': artist.avatar_url,
				'permalink_url': artist.permalink_url,
				'username': artist.username,
				'followers_count': artist.followers_count,
				'followings_count': artist.followings_count,
			})

		datapaths.append(combinedProfiles)	
	

	finalresult = {
		'type': results.get('type'), #type is either 'max' or 'target'
		'username': artistUsername,
		'data': datapaths,	 #data is a list of paths, where if type is target, it will be of size 1
		'degree': degreeReq
		}

	emailPath(finalresult, toEmail)	
	logger.info(str(finalresult))
	return jsonify(finalresult)

@app.route('/api/dummy')
def dummyData():
    dummyArtistData = {
		'username': 'lightchasing',
		'data': [{
			'first_name': 'Eren',
			'last_name': 'Fight',
			'full_name': 'Eren Fight',
			'city': 'Calgary',
			'description': None,
			'country': 'Canada',
			'track_count': 0,
			'public_favorites_count': 0,
			'followers_count': 73,
			'followers_count': 585,
			'plan': 'Free',
			'myspace_name': None,
			'discogs_name': None,
			'website_title': None,
			'website': None,
			'reposts_count': 39,
			'comments_count': 0,
			'online': False,
			'likes_count': 0,
			'playlist_count': 0,
			'avatar_url': 'https://i1.sndcdn.com/avatars-000133770577-62m0tb-large.jpg',
			'id': 2725148,
			'kind': 'user',
			'permalink_url': 'http://soundcloud.com/eren-fight',
			'uri': 'https://api.soundcloud.com/users/2725148',
			'username': 'lightchasing',
			'permalink': 'eren-fight',
			'last_modified': '2015/09/20 00:25:35 +0000',

		}, {
				'first_name': 'Alberto',
				'last_name': 'Petrachi',
				'full_name': 'Alberto Petrachi',
				'city': '',
				'description': None,
				'country': 'Italy',
				'track_count': 3,
				'public_favorites_count': 0,
				'followers_count': 37,
				'followers_count': 134,
				'plan': 'Free',
				'myspace_name': None,
				'discogs_name': None,
				'website_title': None,
				'website': None,
				'reposts_count': 4,
				'comments_count': 6,
				'online': False,
				'likes_count': 0,
				'playlist_count': 0,
				'avatar_url': 'https://i1.sndcdn.com/avatars-000023219316-udqkrb-large.jpg',
				'id': 24862334,
				'kind': 'user',
				'permalink_url': 'http://soundcloud.com/alberto-petrachi',
				'uri': 'https://api.soundcloud.com/users/24862334',
				'username': 'Alberto Petrachi DJ',
				'permalink': 'alberto-petrachi',
				'last_modified': '2016/02/16 08:26:03 +0000'
			}, {
				'first_name': 'Allie',
				'last_name': 'Hall ',
				'full_name': 'Allie Hall',
				'city': 'Vancouver ',
				'description': None,
				'country': 'Canada',
				'track_count': 0,
				'public_favorites_count': 0,
				'followers_count': 614,
				'followers_count': 1010,
				'plan': 'Free',
				'myspace_name': None,
				'discogs_name': None,
				'website_title': None,
				'website': None,
				'reposts_count': 7,
				'comments_count': 0,
				'online': False,
				'likes_count': 0,
				'playlist_count': 0,
				'avatar_url': 'https://i1.sndcdn.com/avatars-000135842476-yztutv-large.jpg',
				'id': 143158664,
				'kind': 'user',
				'permalink_url': 'http://soundcloud.com/allie-hall-11',
				'uri': 'https://api.soundcloud.com/users/143158664',
				'username': 'Allie Hall',
				'permalink': 'allie-hall-11',
				'last_modified': '2015/10/25 22:22:49 +0000'
			}, {
				'first_name': None,
				'last_name': None,
				'full_name': '',
				'city': 'Xanten',
				'description': '',
				'country': None,
				'track_count': 14,
				'public_favorites_count': 0,
				'followers_count': 1589,
				'followers_count': 1984,
				'plan': 'Free',
				'myspace_name': None,
				'discogs_name': None,
				'website_title': None,
				'website': None,
				'reposts_count': 0,
				'comments_count': 0,
				'online': False,
				'likes_count': 0,
				'playlist_count': 0,
				'avatar_url': 'https://i1.sndcdn.com/avatars-000086319106-fj4cje-large.jpg',
				'id': 78490566,
				'kind': 'user',
				'permalink_url': 'http://soundcloud.com/lars-d-4',
				'uri': 'https://api.soundcloud.com/users/78490566',
				'username': 'Lars D.',
				'permalink': 'lars-d-4',
				'last_modified': '2016/02/11 21:05:09 +0000'
			}]
	}

    return jsonify(dummyArtistData)


    


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port), threaded=True)

