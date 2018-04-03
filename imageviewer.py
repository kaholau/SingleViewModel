
import sys
from PyQt5.QtCore import (Qt,QPoint,QSize,QDir,QObject,QFileInfo,pyqtSignal)
from PyQt5.QtGui import (QImage,QPainter,QPixmap,QPalette,QKeySequence,QIcon,qRgb)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QAction, QActionGroup, QApplication, QFileDialog, QFrame,
		QLabel, QMainWindow, QMenu, QMessageBox,QScrollArea, QSizePolicy, QVBoxLayout,
		QWidget)
import numpy as np
import cv2 
from matplotlib import pyplot as plt



class ImageViewer(QScrollArea):

	def __init__(self,parent=None):
		super(ImageViewer, self).__init__(parent)
		self.isModified = False
		self.isReady = False
		#Drawing Status
		self.isDrawVanishingLineStart = False
		self.curAxis = None
		self.isMarkReferencePointStart = False
		self.isGenVRMLStart = False

		self.isVanishingPointDone = False
		self.isReferencePointDone = False
		self.isGenVRMLDone = False	

		#store line info
		self.vanishingLines = {'x' : [], 'y' : [], 'z' : [], None:[]} # list of [[start pt, end pt],[]......]
		self.axisColor = {'x' : (255,0,0), 'y' : (0,255,0), 'z' : (0,0,255)}
		self.tempPoint = [] # store 
		self.refGroundList = [] 


		#Mouse activity status
		self.isMousePressed = False
		self.isMouseMove = False

		#Qt widget object
		self.imageWidget = None

		#Opencv image information
		self.cvImg = None # keep this unchanged for undo action
		self.paintBoard = None #Copy of cvImg for drawing

		# Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
		#Qt image information
		self.qImage = None
		self.qImageHieght = 0
		self.qImageWidth = 0
		self.hieghtbound = 0 #Prevent mouse tracking outside image area
		self.widthbound = 0	#Prevent mouse tracking outside image area
		self.imageScaleFactor = 1


		return

	def initForImage(self,fileName):
		self.cvImg = cv2.imread(fileName,cv2.IMREAD_COLOR)
		self.imageWidget = self.widget()
		self.qImage = self.imageWidget.pixmap()
		self.qImageSize = self.imageWidget.pixmap().size()
		self.qImageHieght = self.imageWidget.pixmap().size().height()
		self.qImageWidth= self.imageWidget.pixmap().size().width()
		self.hieghtbound = self.qImageHieght
		self.widthbound = self.qImageWidth
		self.imageScaleFactor = 1
		#self.imageOriginalSize = (,)   
		self.paintBoard = self.cvImg.copy()
		print(self.qImageSize,self.hieghtbound,self.widthbound )

		self.imageWidget.start(fileName)
		self.isReady = True
		return

	def drawVanishingLineStart(self,axis):
		if self.isReady:			
			if not self.isDrawVanishingLineStart :
				print('drawVanishingLineStart :', axis)
				self.curAxis = axis
				self.isDrawVanishingLineStart = True

		return
	def drawVanishingLineDone(self,axis):
		if self.isDrawVanishingLineStart:
			if self.computeVanishingPoint(axis):
				self.isDrawVanishingLineStart = False
				self.curAxis = None
				return True
		return False

	def resize(self, factor):
		self.imageScaleFactor = factor		
		self.hieghtbound = self.qImageHieght * factor
		self.widthbound = self.qImageWidth * factor
		self.imageWidget.resize(factor  * self.qImage.size())
		return

	def normalSize(self):
		self.imageWidget.adjustSize()
		return

	def getOriginalCoordinate(self, event):
		x = event.pos().x()
		y = event.pos().y()
		isGoal = False
		if  x < self.widthbound and y < self.hieghtbound:
			isGoal = True
			x = int(x / self.imageScaleFactor)
			y = int(y / self.imageScaleFactor)

		return isGoal,x,y

	def mousePressEvent(self, event):
		if self.isReady:
			isGoal,x,y = self.getOriginalCoordinate(event)
			if isGoal:
				self.isMousePressed = True
				if self.isDrawVanishingLineStart:
					self.tempPoint.append([x,y])
					#self.drawPoint(self.paintBoard, [x,y])
		return 

	def mouseMoveEvent(self, event):
		if self.isMousePressed and self.isReady:
			isGoal,x,y = self.getOriginalCoordinate(event)
			if isGoal:
				isMouseMove = True
				if self.isDrawVanishingLineStart:
					self.drawVanishingLine(False, self.paintBoard, self.tempPoint[0], [x,y])

		return      

	def mouseReleaseEvent(self, event):
		self.isMousePressed = False
		if self.isReady:
			isGoal,x,y = self.getOriginalCoordinate(event)
			if isGoal:
				if self.isDrawVanishingLineStart:
					self.tempPoint.append([x,y])
					self.drawVanishingLine(True, self.paintBoard, self.tempPoint[0], self.tempPoint[1])
					self.vanishingLines[self.curAxis].append(self.tempPoint)
					self.tempPoint = []
		return  

	def drawPoint(self,img,pt):
		cv2.circle(img,(pt[0],pt[1]), 2, (255,0,0), -1)
		self.qImage = self.get_qimage(img)
		self.imageWidget.setPixmap(self.qImage)
		return

	def drawLine(self,img,sPt,ePt):
		cv2.line(img,(sPt[0],sPt[1]),(ePt[0],ePt[1]),self.axisColor[self.curAxis],2)
		self.qImage = self.get_qimage(img)
		self.imageWidget.setPixmap(self.qImage)
		return

	def drawVanishingLine(self,isConfirm, img,sPt,ePt):
		if isConfirm:
			#it is confirmed when user release the mouse
			img = self.paintBoard 
			isConfirm = False
		else:
			img = self.paintBoard.copy()
		self.drawLine(img,sPt,ePt)
		return

		return

	def computeVanishingPoint(self,axis):
		self.vanishingLines[axis] = [[[276, 148], [214, 295]], [[335, 146], [383, 313]]]
		if len( self.vanishingLines[axis]) > 1 :
			print('vanishingLineList: ', self.vanishingLines[axis])
			pt = self.imageWidget.computeVanishingPoint(self.vanishingLines[axis], axis)
			print('vanishing pt: ',pt)
			self.drawPoint(self.paintBoard,pt)
			return True
		return False

	def get_qimage(self, image: np.ndarray):
		height, width, colors = image.shape
		bytesPerLine = 3 * width
		image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)

		image = image.rgbSwapped()
		return QPixmap.fromImage(image)

	def clean(self):
		if self.isReady:
			self.vanishingLines = []
			self.tempPoint = [] 
			self.refGroundList = [] 
			self.paintBoard = self.cvImg.copy()
			self.qImage = self.get_qimage(self.paintBoard)
			self.imageWidget.setPixmap(self.qImage)
		return

	def isModified(self):
		return self.modified

