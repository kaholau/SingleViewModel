import sys
from PyQt5.QtCore import (Qt,QPoint,QSize,QDir,QObject,QFileInfo,pyqtSignal)
from PyQt5.QtGui import (QImage,QPainter,QPixmap,QPalette,QKeySequence,QIcon,qRgb)
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QAction, QActionGroup, QApplication, QFileDialog, QFrame,
		QLabel, QMainWindow, QMenu, QMessageBox,QScrollArea, QSizePolicy, QVBoxLayout,
		QWidget)
import imageviewer
import image
		

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.root = QFileInfo(__file__).absolutePath()
		self.curFile = ''


		self.graphicsView = imageviewer.ImageViewer()#QScrollArea()
		self.graphicsView.setMouseTracking(False)
		self.graphicsView.setBackgroundRole(QPalette.Dark)
		#self.graphicsView.setWidget(self.imageLabel)
		self.setCentralWidget(self.graphicsView)

		self.setWindowTitle("Single view modeling")
		self.setGeometry(100, 100, 680, 480)
		self.setMinimumSize(680,480)

		self.curFile = ''
		self.isModified = False

		self.createActions()
		self.createMenus()
		self.createToolBars()
		self.createStatusBar()


		self.drawVanishingLineXAct.setEnabled(False)
		self.drawVanishingLineYAct.setEnabled(False)
		self.drawVanishingLineZAct.setEnabled(False)
		self.markReferencePointAct.setEnabled(False)
		self.genVRMLAct.setEnabled(False)

		self.cleanAct.setEnabled(False)
		self.normalSizeAct.setEnabled(False)
		self.zoomInAct.setEnabled(False)
		self.zoomOutAct.setEnabled(False)	
				
		return

	def eventFilter(self, obj, event):
		print(event.type())
		return False

		
	def createStatusBar(self):
		self.statusBar().showMessage("Ready")
		return
	#===========================Menu>File Action Funtion===================================#
	def open(self):

		#fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", QDir.currentPath())
		fileName = self.root + '/picture/parallel1.jpg'
		if fileName:
			qimage = QImage(fileName)
			if qimage.isNull():
				QMessageBox.information(self, "Single view modeling",
						"Cannot load %s." % fileName)
				return
			self.setCurrentFile(fileName)
			imageLabel = image.Image()#QLabel()
			imageLabel.setBackgroundRole(QPalette.Base)
			imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
			imageLabel.setScaledContents(True)
			imageLabel.setPixmap(QPixmap.fromImage(qimage))

			self.graphicsView.setWidget(imageLabel)
			self.graphicsView.initForImage(fileName)
			self.scaleFactor = 1.0
			self.normalSize()
			self.drawVanishingLineXAct.setEnabled(True)
			self.cleanAct.setEnabled(True)
			self.normalSizeAct.setEnabled(True)
			self.zoomInAct.setEnabled(True)
			self.zoomOutAct.setEnabled(True)

			print(self.getCurrentFile())
		return

	def maybeSave(self):
		if self.graphicsView.isModified():
			ret = QMessageBox.warning(self, "Single view modeling",
						"The image has been modified.\n"
						"Do you want to save your changes?",
						QMessageBox.Save | QMessageBox.Discard |
						QMessageBox.Cancel)
			if ret == QMessageBox.Save:
				return self.save()
			elif ret == QMessageBox.Cancel:
				return False

		return True

	def save(self,case):
		if not self.getCurrentFile():
			return

		fileFormat ='png'
		initialPath = QDir.currentPath() + self.getCurrentFile()+'*.' + fileFormat
		fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
				"%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
		if fileName:
			if not self.graphicsView.widget().pixmap().save(fileName):
				QMessageBox.warning(self, self.tr("Save Image"),self.tr("Failed to save file at the specified location."))
				return
			self.statusBar().showMessage("File saved", 2000)
		
		return


	def exit(self):
		exit()
		return

	#===========================Menu>Edit Action Function================================#
	def clean(self):
		self.graphicsView.clean()
		return

	def undo(self):
		if not self.getCurrentFile():
			return
		self.graphicsView.undo()
		return
	

	#==========================Menu>View Action Function===========================#

	def zoomIn(self):
		self.scaleImage(1.25)
		return
	def zoomOut(self):
		self.scaleImage(0.8)
		return

	def normalSize(self):
		#self.imageLabel.adjustSize()
		self.scaleFactor = 1.0
		self.graphicsView.normalSize()
		return
			
	def orignalImg(self):
		self.graphicsView.displayOriginalImg()
		return

	def imgWithContour(self):
		self.graphicsView.displayImgWithContour()
		return

	def maskedImg(self):
		self.graphicsView.displayMaskedImg()
		return

	def costGraph(self):
		self.graphicsView.displayCostGraph()
		return

	def pathTree(self):
		self.graphicsView.displayPathTreeGraph()
		return
	
	#=========================Menu>Action Action Function================================#

	def drawVanishingLineX(self):
		print('drawVanishingLineX')
		self.graphicsView.drawVanishingLineStart('x')
		if self.graphicsView.drawVanishingLineDone('x'):
			self.drawVanishingLineYAct.setEnabled(True)
		return

	def drawVanishingLineY(self):
		print('drawVanishingLineY')
		self.graphicsView.drawVanishingLineStart('y')
		if self.graphicsView.drawVanishingLineDone('y'):
			self.drawVanishingLineZAct.setEnabled(True)
		return

	def drawVanishingLineZ(self):
		print('drawVanishingLineZ')
		self.graphicsView.drawVanishingLineStart('z')
		if self.graphicsView.drawVanishingLineDone('z'):
			self.markReferencePointAct.setEnabled(True)
		return

	def markReferencePoint(self):
		print('markReferencePoint')
		self.graphicsView.markReferencePointStart(True)
		if self.graphicsView.markReferencePointDone():
			self.genVRMLAct.setEnabled(True)
		return

	def genVRML(self):
		print('genVRML')
		self.graphicsView.genVRMLStart(True)
		if self.graphicsView.genVRMLDone(True):
			print('genVRML done')
		return



	#========================Menu>About Action Function===================================#
	def about(self):
		print('about')
		about = '1. Open file to enable iScissor Start button \
				\n2. Press iScissor Start button and wait few seconds \
				\n3. Press and release mouse left button to mark the first seed on image \
				\n4. Press and move without release mouse can preview contour for other seeds \
				\n5. Press iScissor Done Button to get the masked image'

		QMessageBox.about(self, "About",about)
		return

	def updateActions(self):
		print('updateActions')
		return

	def scaleImage(self, factor):
		
		self.scaleFactor *= factor

		self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
		self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)
		
		self.graphicsView.resize(self.scaleFactor )
		self.adjustScrollBar(self.graphicsView.horizontalScrollBar(), factor)
		self.adjustScrollBar(self.graphicsView.verticalScrollBar(), factor)

		return

	def adjustScrollBar(self, scrollBar, factor):
		scrollBar.setValue(int(factor * scrollBar.value()
								+ ((factor - 1) * scrollBar.pageStep()/2)))

	def getCurrentFile(self):
		return self.curFile

	def setCurrentFile(self, fileName):
		self.curFile = fileName
		self.setModified(False)
		self.setWindowTitle("%s[*] - Single view modeling" % fileName)
		#self.setWindowTitle("%s[*] - iScissor" % QFileInfo(fileName).fileName())
		return
	def setModified(self,modified):
		self.isModified = modified
		return

	#==============================GUI Set Up=====================================================#
	def createActions(self):
		
		#===============================File===================================#
		self.openAct = QAction(QIcon(self.root + '/icon/open.png'),"&Open...", self, shortcut="Ctrl+O",
				statusTip="Open an existing Image", triggered=self.open)

		self.saveAct = QAction(QIcon(self.root + '/icon/save.png'),"&Save", self, shortcut="Ctrl+S",
				statusTip="Save the Image to disk", triggered=self.save)

		self.exitAct = QAction(QIcon(self.root + '/icon/exit.png'),"&Exit", self, shortcut="Ctrl+Q",
				statusTip="Exit the application", triggered=self.exit)


		#================================Edit================================#

		self.cleanAct = QAction(QIcon(self.root + '/icon/clean.png'),"&Clean", self, shortcut="Ctrl+Z",
				statusTip="Click and clean the unwanted paint", triggered=self.clean)


		#================================View================================#

		self.zoomInAct = QAction(QIcon(self.root + '/icon/zoomIn.png'),"&Zoom In", self, shortcut="Ctrl++",
				statusTip="Zoom In",
				triggered=self.zoomIn)

		self.zoomOutAct = QAction(QIcon(self.root + '/icon/zoomOut.png'),"&Zoom Out", self, shortcut="Ctrl+-",
				statusTip="Zoom Out",
				triggered=self.zoomOut)

		self.normalSizeAct = QAction(QIcon(self.root + '/icon/normalSize.png'),"&Normal Size", self, shortcut="Ctrl+N",
				statusTip="Normal Size",
				triggered=self.normalSize)			

		#================================Action================================#

		self.drawVanishingLineXAct = QAction(QIcon(self.root + '/icon/x.png'), "drawVanishingLineX", self, shortcut="1",
		statusTip="&Draw at least 2 vanishing lines for X axis",triggered=self.drawVanishingLineX)

		self.drawVanishingLineYAct = QAction(QIcon(self.root + '/icon/y.png'), "drawVanishingLineY", self, shortcut="1",
		statusTip="&Draw at least 2 vanishing lines for Y axis",triggered=self.drawVanishingLineY)

		self.drawVanishingLineZAct = QAction(QIcon(self.root + '/icon/z.png'), "drawVanishingLineZ", self, shortcut="1",
		statusTip="&Draw at least 2 vanishing lines for Z axis",triggered=self.drawVanishingLineZ)

		self.markReferencePointAct = QAction(QIcon(self.root + '/icon/g.png'), "markReferencePoint", self, shortcut="2",
		statusTip="&Mark Points on ground floor",triggered=self.markReferencePoint)

		self.genVRMLAct = QAction(QIcon(self.root + '/icon/done.png'),"&Generate VRML", self, shortcut="2",
		statusTip="genVRMLAct",triggered=self.genVRML)


		#===============================About===================================#
		self.aboutAct = QAction("&About", self,
				statusTip="Show the application's About box",
				triggered=self.about)

		return

	def createMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File")
		self.fileMenu.addAction(self.openAct)
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.editMenu = self.menuBar().addMenu("&Edit")
		self.editMenu.addAction(self.cleanAct)

		self.editMenu = self.menuBar().addMenu("&View")
		self.editMenu.addAction(self.normalSizeAct)
		self.editMenu.addAction(self.zoomInAct)
		self.editMenu.addAction(self.zoomOutAct)


		self.editMenu = self.menuBar().addMenu("&Action")

		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.aboutAct)
		return

	def createToolBars(self):
		self.fileToolBar = self.addToolBar("File")
		self.fileToolBar.addAction(self.openAct)
		self.fileToolBar.addAction(self.saveAct)

		self.editToolBar = self.addToolBar("Edit")
		self.editToolBar.addAction(self.cleanAct)

		self.editToolBar = self.addToolBar("View")
		self.editToolBar.addAction(self.normalSizeAct)
		self.editToolBar.addAction(self.zoomInAct)
		self.editToolBar.addAction(self.zoomOutAct)


		self.editToolBar = self.addToolBar("Edit")
		self.editToolBar.addAction(self.drawVanishingLineXAct)
		self.editToolBar.addAction(self.drawVanishingLineYAct)
		self.editToolBar.addAction(self.drawVanishingLineZAct)
		self.editToolBar.addAction(self.markReferencePointAct)
		self.editToolBar.addAction(self.genVRMLAct)  

