import cv2 
from PyQt5.QtWidgets import QLabel
import numpy as np
import vanish as v
class Image(QLabel):
	def __init__(self):
		super(Image, self).__init__()	
		self.cvImg = None
		self.cvImgH = 0
		self.cvImgW = 0
		self.configFile = ''
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
	     
