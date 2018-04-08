
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
		self.isRestore = False

		#Drawing Status
		self.isDrawParallelLineStart = False
		self.curAxis = None
		self.isMarkReferencePointStart = False
		self.isGenVRMLStart = False

		self.isVanishingPointDone = False
		self.isReferencePointDone = False
		self.isGenVRMLDone = False	

		#store line info
		#self.parallelLines = {'x' : [], 'y' : [], 'z' : [], None:[]} # list of [[start pt, end pt],[]......]
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

		self.debugOn = False
		return

	def setDebug(self,isDebug):
		self.debugOn = isDebug

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
		fileName = fileName[:-(fileName[::-1].index('.'))] + 'json'
		config = self.imageWidget.initConfig(fileName)
		self.isReady = True
		return

	def drawStart(self,act):

		if self.isReady:
			self.isDrawParallelLineStart = False
			self.isMarkReferencePointStart = False
			if act in ['x', 'y', 'z']:
				self.cleanPaintBoard() 
				self.drawParallelLineStart(act)
			elif act == 'r':
				self.cleanPaintBoard() 
				print('TODO: ref point')
			elif act == '3d':
				self.cleanPaintBoard() 
				self.genVRMLStart()
		else:
			print('no image')		
		
		return 

	def cleanPaintBoard(self):
		self.paintBoard = self.cvImg.copy()
		self.show(self.paintBoard)
		return

	def drawParallelLineStart(self,axis):	
		if not self.isDrawParallelLineStart :
			self.curAxis = axis
			self.isDrawParallelLineStart = True
			print('drawParallelLineStart :', axis)
			lines = self.imageWidget.getParallelLine(axis)
			if len(lines) > 0 :
				for p in lines:
					self.drawParallelLine(True, p[0], p[1])
			

		return

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
				if self.isDrawParallelLineStart:
					self.tempPoint.append([x,y])
					#self.drawPoint(self.paintBoard, [x,y])
		return 

	def mouseMoveEvent(self, event):
		if self.isMousePressed and self.isReady:
			isGoal,x,y = self.getOriginalCoordinate(event)
			if isGoal:
				isMouseMove = True
				if self.isDrawParallelLineStart:
					self.drawParallelLine(False, self.tempPoint[0], [x,y])

		return      

	def mouseReleaseEvent(self, event):
		self.isMousePressed = False
		if self.isReady:
			isGoal,x,y = self.getOriginalCoordinate(event)
			if isGoal:
				if self.isDrawParallelLineStart:
					self.tempPoint.append([x,y])
					self.drawParallelLine(True, self.tempPoint[0], self.tempPoint[1])
					self.imageWidget.addParallelLine(self.curAxis, self.tempPoint)
					self.tempPoint = []
		return  

	def drawPoint(self,img,pt):
		cv2.circle(img,(int(pt[0]),int(pt[1])), 2, (255,0,0), -1)
		self.show(img)
		return

	def drawLine(self,img,sPt,ePt):
		cv2.line(img,(int(sPt[0]),int(sPt[1])),(int(ePt[0]),int(ePt[1])),self.axisColor[self.curAxis],2)
		self.show(img)
		return

	def drawParallelLine(self,isConfirm,sPt,ePt):
		if isConfirm:
			#it is confirmed when user release the mouse
			img = self.paintBoard 
			isConfirm = False
		else:
			img = self.paintBoard.copy()
		self.drawLine(img,sPt,ePt)
		return

		return

	def genVRMLStart(self):
		img = self.paintBoard
		if self.imageWidget.compute3Dmodel():
			V = self.imageWidget.getVanishingPoints()
			print('draw vanishing point:',V)
			for p in V:
				if len(p)>1:
					self.drawPoint(img,p)
			print('genVRML done')
		self.show(img)
		return 

	def get_qimage(self, image: np.ndarray):
		height, width, colors = image.shape
		bytesPerLine = 3 * width
		image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)

		image = image.rgbSwapped()
		return QPixmap.fromImage(image)

	def show(self,img):
		self.qImage = self.get_qimage(img)
		self.imageWidget.setPixmap(self.qImage)
		return

	def clean(self, act):
		if self.isReady:
			self.tempPoint = []
			self.imageWidget.clean(act)
			self.cleanPaintBoard()
		return

	def isModified(self):
		return self.modified

