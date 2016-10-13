import xml.etree.ElementTree as ET
from math import *
import pygame
import threading
import time
import os
import datetime

# ================================================================================
class audioSt(object) :
	""" audioSt class """

	def __init__(self, id, path, position, size, loop, active, volume, action) :
		""" Settings initialization """

		self.__id = id
		self.__path = path
		try:
			self.__uid = int(position)
		except ValueError:
			self.__location = position.split(":")  # table : latitude in tab[0] ; longitude in tab[1]
			self.__latitude = float(self.location[0])
			self.__longitude = float(self.location[1])
			self.__size = float(size)
		self.__loop = True if (loop == "on") else False
		self.__active = True if (active == "on") else False
		self.__volume = int(volume)
		self.__name = action['name']
		self.__comment = action['comment']
		self.__startEvent = action['startEvent']  # list of dict,  ex : [ {	target="Tang11" action="size" size="0"  },
		#																{	target="Tang15" action="size" size="0"  },
		#																{	target="Fond" action="pause"			}]
		self.__outEvent = action['outEvent']  # list of dict
		self.__endEvent = action['endEvent']  # list of dict

	# ------------------------
	@property
	def id(self) :
		return self.__id
	# ------------------------
	@property
	def path(self) :
		return self.__path
	# ------------------------
	@property
	def size(self) :
		return self.__size
	# ------------------------
	def setSize(self, x) :
		self.__size = x
	# ------------------------
	@property
	def loop(self) :
		return self.__loop
	# ------------------------
	@property
	def active(self) :
		return self.__active
	# ------------------------
	def setActive(self, x) :
		self.__active = x
	# ------------------------
	@property
	def volume(self) :
		return self.__volume
	# ------------------------
	@property
	def name(self) :
		return self.__name
	# ------------------------
	@property
	def comment(self) :
		return self.__comment
	# ------------------------
	@property
	def startEvent(self) :
		return self.__startEvent
	# ------------------------
	@property
	def outEvent(self) :
		return self.__outEvent
	# ------------------------
	@property
	def endEvent(self) :
		return self.__endEvent
	# ------------------------
	@property
	def location(self) :
		return self.__location
	# ------------------------
	@property
	def latitude(self) :
		return self.__latitude
	# ------------------------
	@property
	def longitude(self) :
		return self.__longitude
	# ------------------------
	@property
	def uid(self) :
		return self.__uid

# ================================================================================

class Scenario(object):
	""" Scenarios class """

	def __init__(self) :
		""" Settings initialization """
		
		self.listAudio_origin = []
		self.xmlParse('/boot/sonopluie/scenario.xml') # Path to the xml file
		self.listAudio = self.listAudio_origin # Keeping the original list of audioSt in case of reset
		self.activElement = []  # list of activ elements
		
		# Init pygame
		pygame.init()
		pygame.mixer.set_num_channels(len(self.listAudio))
		
		# Starting the checkEndEvent thread
		threading.Thread(target=self.checkEndEvent).start()
		
		self.channels = [None] * len(self.listAudio) # Array of channels (1 channel by audioSt)
		self.listIndexEvent = [None] * 8 # Array of indexEvent (pygame allow only 8 user events)
		self.sounds = [] 
		
		print ('Loading audio files...', datetime.datetime.now())
		
		# Loading audio files in memory
		for audio in self.listAudio:
			sound = pygame.mixer.Sound('/boot/sonopluie/sound/'+ audio.path)
			self.sounds.append(sound)
			
		print ('Loaded !', datetime.datetime.now())

	def resetScenario(self):
		""" Reset the scenario """
		
		for audio in self.listAudio:
			self.stopAudio(audio)
			
		self.listAudio = self.listAudio_origin
		self.listIndexEvent = [None] * 8
		self.activElement = []
		
		print ('Scenario reset')
		
	# ------------------------
	def xmlParse(self, path) :
		""" Parse the XML file : create classes 'audioSt' and an array of classes """
		
		tree = ET.parse(path)
		root = tree.getroot()
		for child in root[2 :] :  # '2:' because the first two are empty on this file, otherwise put 'root' alone
			dic = child.attrib
			name, comment = '', ''
			dicStartEvent, dicOutEvent, dicEndEvent = [], [], []
			for elem in child :
				if elem.tag == "name" :
					name = child.find('name').text
				elif elem.tag == "comment" :
					comment = child.find('comment').text
				elif elem.tag == "startEvent" :
					dicStartEvent.append(elem.attrib)
				elif elem.tag == "outEvent" :
					dicOutEvent.append(elem.attrib)
				elif elem.tag == "endEvent" :
					dicEndEvent.append(elem.attrib)
			actions = {'name' : name, 'comment' : comment, "startEvent" : dicStartEvent, "outEvent" : dicOutEvent, "endEvent" : dicEndEvent}
			try:
				position = dic['uid']
				size = None
			except KeyError:
				position = dic['location']
				size = dic['size']
			
			self.listAudio_origin.append(audioSt(dic['id'], dic['path'],  position, size, dic['loop'], dic['active'], dic['volume'], actions))

	def checkEndEvent(self):
		""" Checking if a song end """
		while True:
			for event in pygame.event.get(): # Waiting for a new pygame event
				eventId = event.type - pygame.USEREVENT
				
				if eventId >= 0 and self.listIndexEvent[eventId] is not None: # If the id of the event correspond to a channel 
					print ("End of", self.listAudio[self.listIndexEvent[eventId]].path)
					self.endEvent(self.listAudio[self.listIndexEvent[eventId]])
						
			time.sleep(0.1) # Check each 0.1 seconds to reduce cpu usage

	
	def calculGps(self, latitude, longitude):
		""" Calcule if the current position is in the ray of a SoundTrack before action """
		
		# Approximate radius of earth in km
		R = 6373.0

		lat1 = radians(latitude)
		lon1 = radians(longitude)
		
		for audio in self.listAudio :
			try:
				# Measuring distance to the audio trigger
				# ===================================== #
				lat2 = radians(audio.latitude)
				lon2 = radians(audio.longitude)
				
				dlon = lon2 - lon1
				dlat = lat2 - lat1

				a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
				c = 2 * atan2(sqrt(a), sqrt(1 - a))

				distance = R * c * 1000	# Get the distance in meter
				
				# If we are in the scope of the audio trigger
				if distance <= audio.size:
					if audio not in self.activElement : # If the audioSt is not already in active element
						self.stopBeacon()	# if there is at least 1 match, we stop all beacon audioSt
						self.startEvent(audio)
						
				# If we are out of the scope of the audio + 3 meter
				if distance > audio.size + 3:
					if audio in self.activElement : # If the audioSt was in active element
						self.outEvent(audio)
			except AttributeError:
				pass
	# ------------------------
	def calculBeacon(self, x) :
		# If a beacon is detected
		for audio in self.listAudio :
			try:
				# Match the audio trigger corresponding to the beacon
				if audio.uid == x :
					if audio.active and audio not in self.activElement : # If the audioSt is not already in active element
						self.stopGps()
						self.startEvent(audio)
				else :
					if audio in self.activElement : # If the audioSt was in active element
						self.outEvent(audio)
			except AttributeError:
				pass
	# ------------------------
	def startEvent(self, audio):
		if audio not in self.activElement:
			self.activElement.append(audio)
		
		if audio.startEvent :
			for elem in audio.startEvent :
				self.event(elem)
				
		self.playAudio(audio)
	# ------------------------
	def outEvent(self, audio) :
		if audio.outEvent :
			for elem in audio.outEvent :
				self.event(elem)
				
	# ------------------------
	def endEvent(self, audio) :
		index = self.listAudio.index(audio)
		self.releaseIndexEvent(index)

		if audio.endEvent :
			for elem in audio.endEvent :
				self.event(elem)
	
	# ------------------------
	def event(self, elem):
		""" Récupère les actions a effectuer """
		target = None
		for audio in self.listAudio :
			if audio.id == elem["target"] :
				target = audio
				break
				
		if target is not None:
			action = elem["action"]
			if action == "size" :
				target.setSize(float(elem["size"]))
			elif action == "play" :
				if target not in self.activElement:
					self.startEvent(target)
			elif action == "pause" :
				if target in self.activElement:
					self.stopAudio(target)
					self.activElement.remove(target)
			elif action == "active":
				target.setActive(True if (elem["state"] == "on") else False)

	# ------------------------
	def playAudio(self, audio):
		index = self.listAudio.index(audio) # Get the index of the audioSt in the list
		
		# If the channel is already playing the audioSt
		if self.channels[index] is not None and self.channels[index].get_busy():
			return 
			
		# If the sound had to be played looped
		loop = -1 if (audio.loop) else 0

		# Get an indexEndEvent (pygame allow only 8 user events)
		indexEvent = self.getIndexEvent(index)
		volume = audio.volume / 100
		
		self.channels[index] = pygame.mixer.Channel(index) # Creating/Erasing a new Channel for the sound
		self.channels[index].play(self.sounds[index], loop, 0, 2000) # Start the playback => Class Channel.play(Sound sound, int loop, int maxtime, int fadeIn)
		self.channels[index].set_volume(volume, volume) # Setting the volume to the left and right channel

		# If the song had not to be played looped
		if loop == 0:
			self.channels[index].set_endevent(pygame.USEREVENT + indexEvent)	# We put an endEvent for this channel
		
		print("play", audio.path)
	
	def stopAudio(self, audio):
		index = self.listAudio.index(audio)
		
		if self.channels[index] is not None:
			if self.channels[index].get_busy(): # If the sound is playing
				self.channels[index].fadeout(2) # Stop the sound by fading on 2 seconds
				print("pause", audio.path)

	def getIndexEvent(self, indexAudio):
		for i in range(0, len(self.listIndexEvent)):
			if self.listIndexEvent[i] is None:
				self.listIndexEvent[i] = indexAudio
				break
			
		index = self.listIndexEvent.index(indexAudio)

		return index
		
	def releaseIndexEvent(self, indexAudio):
		for i in range(0, len(self.listIndexEvent)):
			if self.listIndexEvent[i] is indexAudio:
				self.listIndexEvent[i] = None
				break
		
	# ------------------------
	def stopGps(self):
		for audio in self.activElement:
			try:
				if audio.location :
					self.outEvent(audio)
			except AttributeError:
				pass

	# ------------------------
	def stopBeacon(self):
		for audio in self.activElement:
			try:
				if audio.uid :
					self.outEvent(audio)
			except AttributeError:
				pass
