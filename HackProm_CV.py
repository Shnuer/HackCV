from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import imutils
import cv2
import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QSizePolicy, QLayout, QGridLayout, QSpacerItem, QApplication
from PyQt5.QtGui import QPixmap, QPicture, QPainter, QColor, QFont, QPen, QImage
from PyQt5.QtCore import Qt, QPoint

class GUI(QWidget):
	imageW = 800
	imageH = 800
	imageScale = 1.5
	currentPos = QPoint()
	lastPos = QPoint()

	roix1 = 0
	roiy1 = 0
	roix2 = 0
	roiy2 = 0

	showPeople = False
	showCaps = False
	showMotions = False
	showSteam = False

	drawing = False

	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.lastPoint = QPoint()

		self.redLight = QPixmap("redLight.png")
		self.redLight = self.redLight.scaled(30, 30)
		self.grayLight = QPixmap("grayLight.png")
		self.grayLight = self.grayLight.scaled(30, 30)

		layout = QHBoxLayout(self)

		rightBlockLayout = QVBoxLayout(self)

		self.imageLabel = QLabel()
		self.image = QPixmap("image.png")
		self.currentImage = self.image
		

		indicatorsGroupBox = QGroupBox("Индикация", self)
		indicatorsGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
		indicatorsGroupBox.setMinimumSize(280, 200)

		indicatorsGroupLayout = QGridLayout(indicatorsGroupBox)

		self.peopleIndicator = QLabel()
		self.peopleIndicator.setPixmap(self.grayLight)
		self.capsIndicator = QLabel()
		self.capsIndicator.setPixmap(self.grayLight)
		self.motionsIndicator = QLabel()
		self.motionsIndicator.setPixmap(self.grayLight)
		self.steamIndicator = QLabel()
		self.steamIndicator.setPixmap(self.grayLight)

		indicatorsGroupLayout.setColumnStretch(0, 2)
		indicatorsGroupLayout.setColumnStretch(1, 1)
		indicatorsGroupLayout.addWidget(QLabel("Обнаружены люди"), 0, 0)
		indicatorsGroupLayout.addWidget(self.peopleIndicator, 0, 1)
		indicatorsGroupLayout.addWidget(QLabel("Сотрудник без каски"), 1, 0)
		indicatorsGroupLayout.addWidget(self.capsIndicator, 1, 1)
		indicatorsGroupLayout.addWidget(QLabel("Обнаружено движения"), 2, 0)
		indicatorsGroupLayout.addWidget(self.motionsIndicator, 2, 1)
		indicatorsGroupLayout.addWidget(QLabel("Обнаружен пар/дым"), 3, 0)
		indicatorsGroupLayout.addWidget(self.steamIndicator, 3, 1)

		indicatorsGroupBox.setLayout(indicatorsGroupLayout)

		buttonsGroupBox = QGroupBox("Настройки", self)
		buttonsGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
		buttonsGroupBox.setMinimumSize(280, 200)

		buttonsGroupLayout = QVBoxLayout(buttonsGroupBox)

		peopleButton = QPushButton("Детекция людей", self)
		peopleButton.clicked[bool].connect(self.peopleButtonEvent)
		peopleButton.setCheckable(True)
		peopleButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

		capsButton = QPushButton("Детекция людей без касок", self)
		capsButton.clicked[bool].connect(self.capsButtonEvent)
		capsButton.setCheckable(True)
		capsButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

		motionsButton = QPushButton("Детекция движения", self)
		motionsButton.clicked[bool].connect(self.motionsButtonEvent)
		motionsButton.setCheckable(True)
		motionsButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

		steamButton = QPushButton("Детекция пара/дыма", self)
		steamButton.clicked[bool].connect(self.steamButtonEvent)
		steamButton.setCheckable(True)
		steamButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

		buttonsGroupLayout.addWidget(peopleButton)
		buttonsGroupLayout.addWidget(capsButton)
		buttonsGroupLayout.addWidget(motionsButton)
		buttonsGroupLayout.addWidget(steamButton)

		buttonsGroupBox.setLayout(buttonsGroupLayout)

		rightBlockLayout.addWidget(indicatorsGroupBox)
		rightBlockLayout.addWidget(buttonsGroupBox)
		spacer = QSpacerItem(1, 400)
		rightBlockLayout.addItem(spacer)
		layout.addWidget(self.imageLabel)
		layout.addLayout(rightBlockLayout)

		self.setFixedSize(self.imageW + 300, self.imageH)
		self.setWindowTitle('Помошник оператора')
		self.setLayout(layout)
		self.show()


	def peopleButtonEvent(self, pressed):
		self.showPeople = pressed
		if not pressed:
			self.setPeopleAlert(False)

	def capsButtonEvent(self, pressed):
		self.showCaps = pressed
		if not pressed:
			self.setCapsAlert(False)

	def motionsButtonEvent(self, pressed):
		self.showMotions = pressed
		if pressed == False:
			self.setMotionsAlert(False)

	def steamButtonEvent(self, pressed):
		self.showSteam = pressed
		if not pressed:
			self.setSteamAlert(False)

	def mousePressEvent(self, e):
		if e.buttons() == Qt.LeftButton:
			self.update()
			self.drawing = True
			self.currentPos = e.pos()
			self.lastPos = e.pos()

	def mouseReleaseEvent(self, e):
		self.update()
		self.drawing = False
		self.roix2 = e.pos().x()
		self.roiy2 = e.pos().y()
		self.roix1 = self.lastPos.x()
		self.roiy1 = self.lastPos.y()

	def paintEvent(self, event):
		painter = QPainter() 
		painter.begin(self) 
		painter.drawPixmap(self.imageLabel.rect(), self.currentImage) 
		painter.end() 

	def mouseMoveEvent(self, event):
		if self.drawing: 
			self.currentPos = event.pos()
			self.currentImage = QPixmap(self.image)
			painter = QPainter() 
			painter.begin(self.currentImage) 
			painter.setPen(QPen(Qt.green, 3, Qt.SolidLine)) 
			painter.drawRect(self.lastPos.x() * self.imageScale, self.lastPos.y() * self.imageScale, (event.pos().x() - self.lastPos.x()) * self.imageScale, (event.pos().y() - self.lastPos.y()) * self.imageScale) 
			painter.end()
			self.update()


	#Переключение индикаторов		
	def setPeopleAlert(self, alert):
		if alert:
			self.peopleIndicator.setPixmap(self.redLight)
		else:
			self.peopleIndicator.setPixmap(self.grayLight)

	def setCapsAlert(self, alert):
		if alert:
			self.capsIndicator.setPixmap(self.redLight)
		else:
			self.capsIndicator.setPixmap(self.grayLight)

	def setMotionsAlert(self, alert):
		if alert:
			self.motionsIndicator.setPixmap(self.redLight)
		else:
			self.motionsIndicator.setPixmap(self.grayLight)

	def setSteamAlert(self, alert):
		if alert:
			self.steamIndicator.setPixmap(self.redLight)
		else:
			self.steamIndicator.setPixmap(self.grayLight)	

	#Используется для получения координат области интереса (ROI)		
	def getX1(self):
		return int(self.roix1 * self.imageScale)

	def getY1(self):
		return int(self.roiy1 * self.imageScale)

	def getX2(self):
		return int(self.roix2 * self.imageScale)

	def getY2(self):
		return int(self.roiy2 * self.imageScale)

	#Получение конфигураций	
	def isShowPeople(self):
		return self.showPeople

	def isShowCaps(self):
		return self.showCaps

	def isShowMotions(self):
		return self.showMotions

	def isShowSteam(self):
		return self.showSteam
    
    #Метод для передачи изображения на вывод
	def setImage(self, imageData): 
		image = QImage(imageData, imageData.shape[1], imageData.shape[0], QImage.Format_RGB888) 
		self.image = QPixmap.fromImage(image)
		self.image = self.image.scaled(imageData.shape[1], imageData.shape[0])
		self.currentImage = QPixmap(self.image)
		self.update()
		self.imageW = int(imageData.shape[1] / self.imageScale)
		self.imageH = int(imageData.shape[0] / self.imageScale)
		self.setFixedSize(self.imageW + 300, self.imageH)
		painter = QPainter() 
		painter.begin(self.currentImage) 
		painter.setPen(QPen(Qt.green, 3, Qt.SolidLine)) 
		painter.drawRect(self.lastPos.x() * self.imageScale, self.lastPos.y() * self.imageScale, (self.currentPos.x() - self.lastPos.x()) * self.imageScale, (self.currentPos.y() - self.lastPos.y()) * self.imageScale) 
		painter.end()

	def closeEvent(self, event):

		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes |
			QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()



app = QApplication(sys.argv)
gui = GUI()



#Открыть видеофайл
bbox=[0,0,0,0]
cap = cv2.VideoCapture('C:\\videohack\\l_05_persons_0_01.mp4')
#Взять основной кадр
ret, frame1 = cap.read() 
gui.setImage(frame1)
#Бэкграуд
fgbg = cv2.createBackgroundSubtractorMOG2()

#Создание границ интереса(ROI)
#bbox = cv2.selectROI(frame, False)
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
while(1):
	#Взять фрейм
    ret, frame = cap.read()
    cv2.rectangle(frame,(bbox[0],bbox[1]),(bbox[2],bbox[3]),(0,0,255),2)
 
    #Проверка окончания файла
    if ret == True:  
    	
    	#Получаем границы области интереса
        bbox[0] = gui.getX1()
        bbox[1] = gui.getY1()
        bbox[2] = gui.getX2()
        bbox[3] = gui.getY2()
        
        #Проверка включен ли детектор людей
        if gui.isShowPeople():
           
            #Выделение кадра области интересов
            px = frame[bbox[1]:bbox[3],bbox[0]:bbox[2]]
            (rects, weights) = hog.detectMultiScale(px, winStride=(3, 3),padding=(8, 8), scale=1.05)
            if len(rects)==0:
                gui.setPeopleAlert(False)
            else:
                gui.setPeopleAlert(True)
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
            for (xA, yA, xB, yB) in rects:
                cv2.rectangle(frame, (xA+bbox[0], yA+bbox[1]), (xB+bbox[0], yB+bbox[1]), (0, 255, 0), 2)
        #Проверка включен ли детектор движения   
        if gui.isShowMotions():

            #Сравнение с бэкграундом
            fgmask = fgbg.apply(frame)
            
            #Обработка фильтрами медианным и клиппингом 
            fgmask = cv2.medianBlur(fgmask,21)
            ret,fgmask = cv2.threshold(fgmask, 200, 255, 0)
            
            #Выделяем область интереса по значениям полученным ранее, для обработки
            pxresult = fgmask[bbox[1]:bbox[3],bbox[0]:bbox[2]]
            
            #Выделение контуров
            _, contours0, hierarchy = cv2.findContours(pxresult, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

            #Выделение контуров
            if len(contours0)==0:
                gui.setMotionsAlert(False)
            else:
                gui.setMotionsAlert(True)
                
            # перебираем все найденные контуры в цикле 
            for cnt in contours0: 
            	#Вписываем прямоугольник 
                rect = cv2.minAreaRect(cnt) 

                #Поиск четырех вершин прямоугольника 
                box = cv2.boxPoints(rect) 

                #Округление координат
                box = np.int0(box) 

                #Cмещение координат относительно нуля
                box[0][0] += bbox[0]
                box[0][1] += bbox[1]
                box[1][0] += bbox[0]
                box[1][1] += bbox[1]
                box[2][0] += bbox[0]
                box[2][1] += bbox[1]
                box[3][0] += bbox[0]
                box[3][1] += bbox[1]

                #Рисуем прямоугольник на оригинальном кадре
                cv2.drawContours(frame,[box],0,(255,0,0),2)  
        #Отображение обработанного кадра на GUI интерфейсе
        gui.setImage(frame)

        #Сжатие кадра
        frame = imutils.resize(frame, width=min(800, frame.shape[1]))

        #Вывод обработанного кадра в окно
        cv2.imshow('contours', frame) 
        
        
        #Ожидаем нажатие клавиши, если надо выйти
        if cv2.waitKey(30) == 27:
          break
    #Если файл закончился, запускаем заново, можно сделать обработку следующего видео      
    else:
        cap.release()
        cap = cv2.VideoCapture('C:\\videohack\\l_05_persons_0_01.mp4')
        if (cap.isOpened()== False): 
            print("Error opening video stream or file")
            break
cv2.destroyAllWindows()
sys.exit(app.exec_())