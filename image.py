import cv2 
from PyQt5.QtWidgets import QLabel
import numpy as np
import vanish as v
import os
import json
from shutil import copyfile

class Image(QLabel):
	def __init__(self):
		super(Image, self).__init__()	
		self.cvImg = None
		self.cvImgH = 0
		self.cvImgW = 0
		self.config = ''
		self.configFilePath = ''
		self.axisVanishingPoint = {'x':[], 'y':[], 'z':[]}

		return

	def start(self,imgPath):
		self.cvImg = cv2.imread(imgPath,cv2.IMREAD_COLOR)
		self.cvImgH, self.cvImgW, _ = self.cvImg.shape

		#cv2.imshow('image',img)
		#cv2.waitKey()
		#cv2.destroyAllWindows()


		return

	def initConfig(self,configPath):
		self.configFilePath = configPath
		if os.path.exists(configPath):
			with open(configPath) as file:
				content = file.read()
				self.config = json.loads(content)

				return True
		else:
			copyfile('template.json', configPath)
			with open(configPath) as file:
				content = file.read()
				self.config = json.loads(content)
		
		return False

	def getParallelLine(self,axis):
		return self.config[axis]['linePoints']


	def addParallelLine(self,axis,lines):
		''' lines are points  [[x1,y1],[x2,y2]]

		'''	
		self.config[axis]['linePoints'].append(lines)
		return

	def writeConfig(self,layers,value):
		
		return


	def computeVanishingPoint(self, lineList, axis):
		if len(lineList) > 0:
			self.axisVanishingPoint[axis] = v.computeVanishingPoint(self.cvImgH, self.cvImgW, lineList)
			return self.axisVanishingPoint[axis] 
		return None

	def mouseReleaseCallback(self,x,y):
		
		return  

	def mouseMoveCallback(self,x,y):
		return 


	def saveConfig(self):
		open(self.configFilePath, 'w').close()
		with open(self.configFilePath,'r+') as file:
			json.dump(self.config, file, indent = 4)

		self.initConfig(self.configFilePath)
		print('config save to ' + self.configFilePath)
		return

	def clean(self, act):
		if act in ['x','y','z']:
			self.config[act]['linePoints'] = []
			self.config[act]['vanishingPoint'] = []
			print('clean ' + act)

		return
	     
