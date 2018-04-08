import cv2 
from PyQt5.QtWidgets import QLabel
import numpy as np
import svm
import os
import json
from shutil import copyfile
from copy import deepcopy

class Image(QLabel):
	def __init__(self):
		super(Image, self).__init__()	
		self.cvImg = None
		self.cvImgH = 0
		self.cvImgW = 0
		self.config = ''
		self.configFilePath = ''
		self.axis = ['x','y','z']
		return

	def start(self,imgPath):
		self.cvImg = cv2.imread(imgPath,cv2.IMREAD_COLOR)
		self.cvImgH, self.cvImgW, _ = self.cvImg.shape

		#cv2.imshow('image',img)
		#cv2.waitKey()
		#cv2.destroyAllWindows()


		return

	def initConfig(self,configPath):
		'''load the whole json and store as dictionary in image object.
		If not exist, new one will be created
			
		'''
		self.configFilePath = configPath
		print('config: ', self.configFilePath)
		if os.path.exists(configPath):
			with open(configPath) as file:
				content = file.read()
				self.config = json.loads(content)

				return True
		else:
			
			with open(configPath,'w+') as file:
				copyfile('template.json', configPath)
				content = file.read()
				self.config = json.loads(content)
		
		return False

	def saveConfig(self):
		open(self.configFilePath, 'w').close()
		with open(self.configFilePath,'r+') as file:
			json.dump(self.config, file, indent = 4)

		self.initConfig(self.configFilePath)
		print('config save to ' + self.configFilePath)
		return

	def clean(self, act):
		if act in self.axis:
			self.config[act]['linePoints'] = []
			self.config[act]['vanishingPoint'] = []
			print('clean ' + act)

		return		
	def getParallelLine(self,axis):
		''' called by imageviewer for displaying parallel line for corresponding axis

		'''
		return self.config[axis]['linePoints']


	def addParallelLine(self,axis,lines):
		''' lines are points  [[x1,y1],[x2,y2]].
		Called by imageviewr after paralled is drawn for axis.

		'''	
		self.config[axis]['linePoints'].append(lines)
		return


	def computeVanishingPoint(self):
		'''compute vanishing point and stored in dictionary.
		Caution: this config here is not saved in file

		'''
		for axis in self.axis:
			lines = deepcopy(self.config[axis]['linePoints'])
			if len(lines) > 0:
				v = svm.computeVanishingPoint(self.cvImgH, self.cvImgW, lines)
				print(axis + "vanishing point is :"  )
				print(v)
				self.config[axis]['vanishingPoint'] = v
			else:
				print('no vanishingPoint computed for ',axis)	

		return

	def getVanishingPoints(self):
		V = []
		for a in self.axis:
			V.append(self.config[a]['vanishingPoint'])
		return V


	
	     
	def compute3Dmodel(self):
		'''1. Compute vanishing points
		2 . Compute homography H
		3. Compute 3D positions
		4. Output a VRML model

		'''
		self.computeVanishingPoint()

		return True

	def mouseReleaseCallback(self,x,y):
		
		return  

	def mouseMoveCallback(self,x,y):
		return 
	