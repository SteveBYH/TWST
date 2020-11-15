from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from AccelerometerMath import *

class Button():
    def __init__(self, buttonWidth, buttonHeight, xPos, yPos, text, buttonColor = Qt.black, textColor = Qt.white):
        self.buttonWidth = buttonWidth
        self.buttonHeight =  buttonHeight
        self.xPos = xPos
        self.yPos = yPos
        self.text = text
        self.buttonColor = buttonColor
        self.textColor = textColor
        self.clickable = True

    def isClickable(self):
        return self.clickable

    def turnOn(self):
        self.clickable = True

    def turnOff(self):
        self.clickable = False

    def draw(self, qp):
        if self.clickable==True:
            textColorPen = QPen(QBrush(self.textColor), 5)
            buttonColorPen = QPen(QBrush(self.buttonColor), 5)
            qp.setPen(buttonColorPen)
            qp.setBrush(self.buttonColor)
            qp.drawRect(self.xPos, self.yPos, self.buttonWidth, self.buttonHeight)
            qp.setPen(textColorPen)
            qp.drawText(QRect(self.xPos, self.yPos, self.buttonWidth, self.buttonHeight), Qt.AlignCenter, self.text)

    def buttonClicked(self, x, y):
        if self.clickable == False:
            return False
        return(self.xPos<x<self.xPos+self.buttonWidth and self.yPos<y<self.yPos+self.buttonHeight)

    def getX(self):
        return self.xPos

    def getY(self):
        return self.yPos

    def getButtonWidth(self):
        return self.buttonWidth

    def getButtonHeight(self):
        return self.getButtonHeight
