import sys, signal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QImage
from PyQt5.QtCore import Qt, QRect, QLine
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel,QLineEdit
from Button import Button
import math
import time
import threading
from AccelerometerMath import *
from callstepper import *
from statistics import mean
import LIS3DHMOD as acc
import RPi.GPIO as GPIO
import argparse

W_WIDTH = 500
W_HEIGHT = 500


x_list=[]
y_list=[]
z_list=[]

runButton = Button(100,50, W_WIDTH//2-50, W_HEIGHT-250, 'Run')
homeButton = Button(75,25,20,8,'Home')
homeButton.turnOff()
button1 = Button(75,25,W_WIDTH//2+50,W_HEIGHT-200,'1 g')
button1.turnOff()
button10 = Button(75,25,W_WIDTH//2+50,W_HEIGHT-165,'10 g')
button10.turnOff()
button20 = Button(75,25,W_WIDTH//2+50,W_HEIGHT-130,'20 g')
button20.turnOff()
button100 = Button(75,25,W_WIDTH//2+50,W_HEIGHT-95,'100 g')
button100.turnOff()
removeMassButton = Button(75,25,W_WIDTH//2+135,W_HEIGHT-165,'Remove',Qt.red)
removeMassButton.turnOff()
startButton = Button(75,25,W_WIDTH//2+135,W_HEIGHT-130,'Start',Qt.green)
startButton.turnOff()
settingButton = Button(75,25,400,8,'Settings')
settingButton.turnOn()
oneButton = Button(75,25,W_WIDTH//2-110,W_HEIGHT//2- 50,'1')
oneButton.turnOff()
twoButton = Button(75,25,W_WIDTH//2-25,W_HEIGHT//2- 50,'2')
twoButton.turnOff()
threeButton = Button(75,25,W_WIDTH//2+60,W_HEIGHT//2- 50,'3')
threeButton.turnOff()
fourButton = Button(75,25,W_WIDTH//2-110,W_HEIGHT//2- 15,'4')
fourButton.turnOff()
fiveButton = Button(75,25,W_WIDTH//2-25,W_HEIGHT//2- 15,'5')
fiveButton.turnOff()
sixButton = Button(75,25,W_WIDTH//2+60,W_HEIGHT//2- 15,'6')
sixButton.turnOff()
sevenButton = Button(75,25,W_WIDTH//2-110,W_HEIGHT//2+20,'7')
sevenButton.turnOff()
eightButton = Button(75,25,W_WIDTH//2-25,W_HEIGHT//2+20,'8')
eightButton.turnOff()
nineButton = Button(75,25,W_WIDTH//2+60,W_HEIGHT//2+20,'9')
nineButton.turnOff()
delButton = Button(75,25,W_WIDTH//2-110,W_HEIGHT//2+55,'del')
delButton.turnOff()
zeroButton = Button(75,25,W_WIDTH//2-25,W_HEIGHT//2+55,'0')
zeroButton.turnOff()
setButton = Button(75,25,W_WIDTH//2+60,W_HEIGHT//2+55,'set')
setButton.turnOff()
pointButton = Button(75,25,W_WIDTH//2-25,W_HEIGHT//2+90,'.')
pointButton.turnOff()
buttonList = [pointButton,runButton,button1,button10,button20,button100,homeButton,removeMassButton,startButton,settingButton,oneButton,twoButton,threeButton,fourButton,fiveButton,sixButton,sevenButton,eightButton,nineButton,delButton,zeroButton,setButton]

class main_screen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Centripetal Force')
        self.setGeometry(610, 300, W_WIDTH,W_HEIGHT)
        self.circle_Xcoord = W_WIDTH//2-25
        self.circle_Ycoord = W_HEIGHT//2-145
        self.rod_Xcoord = W_WIDTH//2
        self.rod_Ycoord = W_HEIGHT//2-30
        self.angle = 270
        self.reset = False
        self.displayResults = False
        self.errorScreen = False
        self.settingScreen = False
        self.period = .7
        self.calc = None
        self.force = 0
        self.xinit = 0
        self.yinit = 0
        self.zinit = 0

        self.text = 'Click the button to find Centripetal Force'
        self.topLabel = QLabel(self.text,self)
        self.topLabel.move(W_WIDTH//2-167,30)
        self.topLabel.setAlignment(Qt.AlignCenter)
        self.topLabel.setStyleSheet("background-color: black; border: none; color: white; font: bold 16px; border-style: outset;border-radius: 10px;")
        self.topLabel.setGeometry(W_WIDTH//2-167,40,334,50)

        try:
            self.setUpAccel()
        except:
            self.text = 'You set up the accelerometer wrong!'
            runButton.turnOff()
            homeButton.turnOn()

        self.massScreen = False
        self.massesEntered = False
        self.massArray = []
        self.mass = 0
        self.show()

    def paintEvent(self, event):
        self.topLabel.setText(self.text)
        qp = QPainter()
        qp.begin(self)

        qp.setPen(QPen(QBrush(Qt.black),5))
        qp.setFont(QFont('Times', 16))
        
        if self.settingScreen == False:
            qp.drawLine(QLine(self.rod_Xcoord,self.rod_Ycoord,self.circle_Xcoord+25,self.circle_Ycoord+25))
            qp.setBrush(QBrush(Qt.black, Qt.SolidPattern))
            qp.drawEllipse(self.circle_Xcoord,self.circle_Ycoord,50,50)

        for item in buttonList:
            item.draw(qp)

        if self.settingScreen == False:
            if self.massScreen == True:
                qp.setPen(QPen(QBrush(Qt.blue), 2))
                qp.setBrush(QBrush(Qt.blue))
                qp.drawRect(75,W_HEIGHT-70,100,10)
                qp.setPen(QPen(QBrush(Qt.black),2))
                qp.drawRect(75,W_HEIGHT-70,100,10)
                drawNextMassY = W_HEIGHT-70
                for item in self.massArray:
                    qp.setBrush(QBrush(Qt.gray))
                    if item == 1:
                        height = 6
                    elif item == 10:
                        height = 15
                    elif item == 20:
                        height = 30
                    else:
                        height = 45
                    qp.drawRect(85,drawNextMassY-(height),80,height)
                    drawNextMassY = drawNextMassY-(height)
                    qp.drawText(90,W_HEIGHT-30,'Mass: '+str(self.mass)+' g')
        else:
            qp.setPen(QPen(QBrush(Qt.black), 3))
            qp.drawText(150,400,'Period: '+str(self.period) +' s')
            if self.calc != None:
                qp.drawText(200,150,str(self.calc))

        if self.displayResults == True:
            qp.setPen(QPen(QBrush(Qt.black), 2))
            if self.force == 0:
                qp.drawText(125,250,'Calculating...')
            else:
                if isinstance(self.force,str)==False:
                    qp.drawText(125,250,'Centripetal Force: '+str(round(self.force,2))+' N')
                    qp.drawText(125,300,'Mass: '+str(self.mass)+' g')
                    qp.drawText(125,350,'Period: '+str(self.period)+' s')
                else:
                    
                    qp.drawText(125,250,'Centripetal Force: '+self.force)
                    qp.drawText(125,300,'Mass: '+str(self.mass)+' g')

    def mousePressEvent(self, event):
        xCord = event.x()
        yCord = event.y()

        if settingButton.buttonClicked(xCord,yCord):
            self.settingScreen = True
            self.text = 'Settings'
            homeButton.turnOn()
            runButton.turnOff()
            settingButton.turnOff()
            button1.turnOff()
            button10.turnOff()
            button20.turnOff()
            button100.turnOff()
            removeMassButton.turnOff()
            startButton.turnOff()
            oneButton.turnOn()
            twoButton.turnOn()
            threeButton.turnOn()
            fourButton.turnOn()
            fiveButton.turnOn()
            sixButton.turnOn()
            sevenButton.turnOn()
            eightButton.turnOn()
            nineButton.turnOn()
            delButton.turnOn()
            zeroButton.turnOn()
            setButton.turnOn()
            pointButton.turnOn()
            self.update()

        if homeButton.buttonClicked(xCord,yCord):
            runButton.turnOn()
            settingButton.turnOn()
            homeButton.turnOff()
            button1.turnOff()
            button10.turnOff()
            button20.turnOff()
            button100.turnOff()
            removeMassButton.turnOff()
            oneButton.turnOff()
            twoButton.turnOff()
            threeButton.turnOff()
            fourButton.turnOff()
            fiveButton.turnOff()
            sixButton.turnOff()
            sevenButton.turnOff()
            eightButton.turnOff()
            nineButton.turnOff()
            delButton.turnOff()
            zeroButton.turnOff()
            setButton.turnOff()
            pointButton.turnOff()
            self.settingScreen = False
            startButton.turnOff()
            self.text = 'Click the button to find Centripetal Force'
            self.mass = 0
            self.calc = None
            self.force = 0
            try:
                self.setUpAccel()
            except:
                self.text = 'You set up the accelerometer wrong!'
                runButton.turnOff()
                homeButton.turnOn()
            self.massScreen = False
            self.displayResults = False
            self.errorScreen = False
            self.reset = True
            self.massesEntered = False
            self.circle_Xcoord = W_WIDTH//2-25
            self.circle_Ycoord = W_HEIGHT//2-145
            self.rod_Xcoord = W_WIDTH//2
            self.rod_Ycoord = W_HEIGHT//2-30
            self.massArray = []
            self.update()

        if runButton.buttonClicked(xCord,yCord):
            runButton.turnOff()
            homeButton.turnOn()
            self.text = 'Enter masses by clicking buttons below.'
            button1.turnOn()
            button10.turnOn()
            button20.turnOn()
            button100.turnOn()
            removeMassButton.turnOn()
            startButton.turnOn()
            self.massScreen = True
            self.update()

        if button1.buttonClicked(xCord,yCord):
            self.massArray.append(1)
            self.mass += 1
            self.update()
        if button10.buttonClicked(xCord,yCord):
            self.massArray.append(10)
            self.mass += 10
            self.update()
        if button20.buttonClicked(xCord,yCord):
            self.massArray.append(20)
            self.mass += 20
            self.update()
        if button100.buttonClicked(xCord,yCord):
            self.massArray.append(100)
            self.mass += 100
            self.update()
        if removeMassButton.buttonClicked(xCord,yCord):
            if len(self.massArray)>0:
                massToRemove = self.massArray.pop()
                self.mass = self.mass - massToRemove
            self.update()
        if startButton.buttonClicked(xCord,yCord):
            self.massesEntered = True
            button1.turnOff()
            button10.turnOff()
            button20.turnOff()
            button100.turnOff()
            removeMassButton.turnOff()
            settingButton.turnOff()
            startButton.turnOff()
            self.countdown_thread = threading.Thread(target=self.countdown, args=())
            self.countdown_thread.start()
            self.animation_thread = threading.Thread(target = self.moveCircle, args=(self.angle,(self.circle_Xcoord,self.circle_Ycoord+90)))
            self.animation_thread.start()

        if oneButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '1'
            else:
                self.calc = '1'
            self.update()

        if twoButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '2'
            else:
                self.calc = '2'
            self.update()

        if threeButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '3'
            else:
                self.calc = '3'
            self.update()

        if fourButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '4'
            else:
                self.calc = '4'
            self.update()

        if fiveButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '5'
            else:
                self.calc = '5'
            self.update()

        if sixButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '6'
            else:
                self.calc = '6'
            self.update()

        if sevenButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '7'
            else:
                self.calc = '7'
            self.update()

        if eightButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '8'
            else:
                self.calc = '8'
            self.update()

        if nineButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '9'
            else:
                self.calc = '9'
            self.update()

        if zeroButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '0'
            else:
                self.calc = '0'
            self.update()

        if pointButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc += '.'
            else:
                self.calc = '.'
            self.update()

        if delButton.buttonClicked(xCord,yCord):
            if self.calc != None:
                self.calc = self.calc[:len(self.calc)-1]
            self.update()

        if setButton.buttonClicked(xCord,yCord):
            if self.calc != None and self.calc != '0':
                try:
                    self.period = float(self.calc)
                    self.calc = None
                    self.text = 'Settings'
                except:
                    self.text = 'You need to enter a number you dolt!'
                    self.calc = None
            if self.calc == '0':
                self.text = 'Please enter a non-zero value!'
                self.calc = None
                    
            
            self.update()

    def runMotor(self):
        # 4-wire bipolar stepper motor - NEMA-17 42BYGHW609
        GPIO.setmode(GPIO.BCM)

        # Enable pins for IN1-4
        control_pin = [4,17,27,22]
        delay = self.period/1390.0 #change for speed

        # IN1-4 pin setup
        for pin in control_pin:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0) #counter-clockwise rotation

        halfstep_seq = [[1,0,0,0],
                        [1,1,0,0],
                        [0,1,0,0],
                        [0,1,1,0],
                        [0,0,1,0],
                        [0,0,1,0],
                        [0,0,0,1],
                        [1,0,0,1]]

        #setting stepper
        timevar = 10.0//delay
        counter = 0
        while counter<timevar:
            for i in range(512):
                if self.reset== True:
                    GPIO.cleanup()
                    break
                for step in range(8):
                    for pin in range(4):
                        GPIO.output(control_pin[pin],halfstep_seq[step][pin])
                    time.sleep(delay)
                    counter += 1
        GPIO.cleanup()

    def moveCircle(self,angle,coordsCirc):
        self.reset = False
        while self.countdown_thread.is_alive():
            pass
            
        stepperThread = threading.Thread(target=self.runMotor, args=())
        stepperThread.start()
        #accelThread = threading.Thread(target=runAccel, args=(stepperThread,accelArray))
        #accelThread.start()
        timeInitial = time.time()
        while 1:
            try:
                if time.time()-timeInitial > 2 and time.time()-timeInitial < 8:
                    x = self.config.getX()
                    y = self.config.getY()
                    z = self.config.getZ()

                    x_list.append(x)
                    y_list.append(y)
                    z_list.append(z)
            except:
                self.errorScreen = True
                self.massScreen = False
                self.text = "Check your wires. Something's amiss!"

            angle += 4
            theta = math.radians(angle)
            self.circle_Xcoord = coordsCirc[0] + (90 * math.cos(theta))
            self.circle_Ycoord = coordsCirc[1] + (90 * math.sin(theta))
            self.update()
            time.sleep(.01)

            if stepperThread.is_alive() == False:
                xmean = mean(x_list)
                ymean = mean(y_list)
                zmean = mean(z_list)
                
                accelArray = [xmean,ymean,zmean]

                accelArray0 = [self.xinit, self.yinit, self.zinit]

                self.circle_Xcoord = W_WIDTH//2-25
                self.circle_Ycoord = W_HEIGHT//2-145
                self.rod_Xcoord = W_WIDTH//2
                self.rod_Ycoord = W_HEIGHT//2-30

                self.displayResults = True
                self.massScreen = False
                self.text = 'Centripetal Force'
                self.update()
                
                #print(accelArray)
                try:
                    self.force = findforce(accelArray,accelArray0,self.mass)
                except:
                    self.force = '''There was an unexpected error'''
                
                self.update()
                break
            
            if self.reset == True:
                self.circle_Xcoord = W_WIDTH//2-25
                self.circle_Ycoord = W_HEIGHT//2-145
                self.rod_Xcoord = W_WIDTH//2
                self.rod_Ycoord = W_HEIGHT//2-30
                break

    def countdown(self):
        while self.massesEntered == False:
            pass
        for i in range(3,0,-1):
            self.text = 'Please Stand Back! Starting in '+str(i)
            self.update()
            time.sleep(1)
            if self.reset == True:
                break
        if self.reset == False:
            self.text = 'Please Stand Back!'

    def setUpAccel(self):
        self.config = acc.LIS3DH()
        self.config.setRange(0b00)
        self.config.setDataRate(0b0101)
        
        self.xinit = self.config.getX()
        self.yinit = self.config.getY()
        self.zinit = self.config.getZ()


def main():
  app = QApplication(sys.argv)
  ex = main_screen()
  sys.exit(app.exec_())
