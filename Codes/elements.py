from PyQt5.QtWidgets import *
import os
import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
import numpy as np
import re


# Every element is a kind of QLabel and we add image to them as their symbols
class element(QLabel):
    def __init__(self, name, parent, value):
        QLabel.__init__(self, parent)
        self.name = name
        self.value = value
        self.nodeP = None
        self.nodeS = None
        self.symbol = None

## Node class -----------------------------------------------

class node(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.id = None
        self.setStyleSheet("background-color:blue")
        self.setFixedSize(10, 10)
        self.connected_elements = set([])  # define set instead of list in order to prevent repeat of elements added

        self.idLabel = QLabel(parent)
        self.idLabel.move(self.x(), self.y() + 20)
        self.idLabel.resize(20, 15)
        self.idLabel.show()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.parent().wireEnable == True:
                self.parent().nodes2beConnected.append(self)
            if self.parent().nodes2beConnected.__len__() == 2 :
                self.parent().nodes2beConnected[0].connected_elements =  self.parent().nodes2beConnected[0].connected_elements.union(
                            self.parent().nodes2beConnected[1].connected_elements)
                self.parent().nodes2beConnected[1].connected_elements = self.parent().nodes2beConnected[0].connected_elements

                #ids of Nodes:
                if self.parent().nodes2beConnected[0].id == None and self.parent().nodes2beConnected[1].id == None :
                    print("Both of the nodes dont have id")
                    self.parent().nodes2beConnected[0].id = self.parent().nodes2beConnected[1].id = 'N%i'%self.parent().node_number
                    # یه دیکشنری تعریف میکنیم که Key آن Id باشد و value  آن اون node هایی است که به هم وصل شده اند
                    self.parent().node_dict['N%i'%self.parent().node_number ] = set(self.parent().nodes2beConnected)
                    self.parent().node_number += 1
                    print(self.parent().nodes2beConnected[0].id )

                    self.parent().nodes2beConnected[0].idLabel.setText(str(self.id))
                    self.parent().nodes2beConnected[0].idLabel.move(self.parent().nodes2beConnected[0].x(),
                                                                    self.parent().nodes2beConnected[0].y() - 15)
                    self.parent().nodes2beConnected[1].idLabel.setText(str(self.id))
                    self.parent().nodes2beConnected[1].idLabel.move(self.parent().nodes2beConnected[1].x(),
                                                                    self.parent().nodes2beConnected[1].y() - 15)

                elif self.parent().nodes2beConnected[0].id is not None and self.parent().nodes2beConnected[1].id is not None :
                    print("Both of the nodes has id")
                    if self.parent().nodes2beConnected[1].id == 'N0':
                        self.parent().node_dict[self.parent().nodes2beConnected[1].id] = \
                            self.parent().node_dict[self.parent().nodes2beConnected[1].id].union(
                                self.parent().node_dict[self.parent().nodes2beConnected[0].id])

                        redundancy = self.parent().nodes2beConnected[0].id

                        for Node in self.parent().node_dict[self.parent().nodes2beConnected[0].id]:
                            Node.id = self.parent().nodes2beConnected[1].id
                            Node.idLabel.setText(str(self.parent().nodes2beConnected[1].id))
                            Node.idLabel.move(Node.x(), Node.y() - 15)

                        print(self.parent().nodes2beConnected[1].id)

                        # Deleting the dict[Node1] of dictionary:
                        del self.parent().node_dict[redundancy]
                    else:
                        #in this case dict[Node0] = dict[Node0] + dict[Node1]
                        self.parent().node_dict[self.parent().nodes2beConnected[0].id] = \
                            self.parent().node_dict[self.parent().nodes2beConnected[0].id].union(
                                self.parent().node_dict[self.parent().nodes2beConnected[1].id])

                        redundancy = self.parent().nodes2beConnected[1].id

                        for Node in self.parent().node_dict[self.parent().nodes2beConnected[1].id] :
                            Node.id = self.parent().nodes2beConnected[0].id
                            Node.idLabel.setText(str(self.parent().nodes2beConnected[0].id))
                            Node.idLabel.move(Node.x(), Node.y() - 15)

                        print(self.parent().nodes2beConnected[0].id)

                        # Deleting the dict[Node1] of dictionary:
                        del self.parent().node_dict[redundancy]

                else:
                    print("Only one of the nodes has id")
                    if self.parent().nodes2beConnected[0].id == None :
                        print("id0 is None")
                        self.parent().nodes2beConnected[0].id = self.parent().nodes2beConnected[1].id
                        # self.parent().node_dict[self.parent().nodes2beConnected[1].id] = \
                        self.parent().node_dict[self.parent().nodes2beConnected[1].id].add(
                            self.parent().nodes2beConnected[0])
                        self.parent().nodes2beConnected[0].idLabel.setText(str(self.parent().nodes2beConnected[1].id))
                        self.parent().nodes2beConnected[0].idLabel.move(self.parent().nodes2beConnected[0].x(),
                                                                        self.parent().nodes2beConnected[0].y() - 15)
                    else:
                        print("id1 is None")
                        self.parent().nodes2beConnected[1].id = self.parent().nodes2beConnected[0].id
                        # self.parent().node_dict[self.parent().nodes2beConnected[0].id] = \
                        self.parent().node_dict[self.parent().nodes2beConnected[0].id].add(
                            self.parent().nodes2beConnected[1])
                        self.parent().nodes2beConnected[1].idLabel.setText(str(self.parent().nodes2beConnected[0].id))
                        self.parent().nodes2beConnected[1].idLabel.move(self.parent().nodes2beConnected[1].x(),
                                                                        self.parent().nodes2beConnected[1].y() - 15)

                    print(self.parent().nodes2beConnected[0].id)

                self.parent().connectNodes()
                # self.parent().wireEnable = False
                self.parent().nodes2beConnected.clear()

## Ground Class -----------------------------------------

class Ground(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.symbol = QPixmap()
        self.symbol.load('gnd.png')
        self.symbol = self.symbol.scaledToWidth(30)
        self.resize(self.symbol.size())
        self.setPixmap(self.symbol)
        self.move(300, 300)
        self.show()

        self.Node = node(parent)
        self.Node.move(self.x() + 10, self.y())
        self.Node.id = 'N0'
        self.Node.show()
        self.parent().node_dict['N0'].add(self)

        # When right click on element a menu pops on
        self.PropMenu = QMenu(parent)
        # self.PropMenu.addAction('Rotate')
        self.PropMenu.addAction('Delete')
        # Setting Geometry of menu
        self.PropMenu.move(parent.frameGeometry().left() + self.x() + 30,
                           parent.frameGeometry().top() + self.y() + 30)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        if event.button() == QtCore.Qt.RightButton:
            action = self.PropMenu.exec()

            if action is not None:
                if action.text() == 'Delete':
                    print('Delete clicked')
                    self.deleteMe()

                # elif action.text() == 'Rotate':
                #     print('Rotate clicked')
                #     # self.Rotate()

        super(Ground, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)

            # Moving element to new position
            self.move(newPos)

            self.Node.move(newPos.x() + 10, newPos.y() )
            self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 30,
                               self.parent().frameGeometry().top() + newPos.y() + 30)

            self.__mouseMovePos = globalPos
        super(Ground, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(Ground, self).mouseReleaseEvent(event)

    def deleteMe(self):
        self.hide()
        self.Node.hide()

## Current Source class -------------------------------------------------

class Current_src(element):
    freq = 1000
    def __init__(self, name, parent, value = 1):
        element.__init__(self, name, parent, value)
        self.Impedance = 1000000

        # adding image to resistor(that is a QLabel object itself) as its symbol
        self.symbol = QPixmap()
        self.symbol.load('current_src.png')
        self.symbol = self.symbol.scaledToWidth(100)
        self.resize(self.symbol.size())
        self.setPixmap(self.symbol)
        self.move(200, 200)

        self.valueText = QLineEdit(parent)
        self.valueText.move(self.x() + 90, self.y() + 40)
        self.valueText.resize(40, 15)
        self.valueText.setText(str(self.value)+ '  A')

        self.idLabel = QLabel(parent)
        self.idLabel.move(self.x() + 90, self.y() + 20)
        self.idLabel.resize(20, 15)
        self.idLabel.setText(str(self.name))
        self.idLabel.show()

        self.impedanceText = QLineEdit(parent)
        self.impedanceText.move(self.x() + 90, self.y() + 60)
        self.impedanceText.resize(80, 15)
        self.impedanceText.setText(str(self.Impedance)+ '  ohm')

        self.freqText = QLineEdit(parent)
        self.freqText.move(self.x() + 90, self.y() + 80)
        self.freqText.resize(60, 15)
        self.freqText.setText(str(Current_src.freq) + '  Hz')

        self.nodeP = node(parent)
        self.nodeS = node(parent)
        self.nodeP.move(self.x() + 45, self.y() + 90)
        self.nodeS.move(self.x() + 45, self.y())
        self.nodeP.show()
        self.nodeS.show()
        # first element tahr is connected to a ned is It's element.
        self.nodeP.connected_elements.add(self.name)
        self.nodeS.connected_elements.add(self.name)

        # When right click on element a menu pops on
        self.PropMenu = QMenu(parent)
        self.PropMenu.addAction('Change Value')
        self.PropMenu.addAction('Rotate')
        self.PropMenu.addAction('Delete')
        # Setting Geometry of menu
        self.PropMenu.move(parent.frameGeometry().left() + self.x() + 20,
                           parent.frameGeometry().top() + self.y() + 100)

        self.direction0 = True
        self.direction1 = True

        self.valueText.show()
        self.impedanceText.show()
        self.freqText.show()
        self.show()

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        if event.button() == QtCore.Qt.RightButton:
            action = self.PropMenu.exec()

            if action is not None:
                if action.text() == 'Change Value':
                    print('Change Value clicked')
                    self.value = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())
                    self.Impedance = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())
                    Current_src.freq = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())

                elif action.text() == 'Rotate':
                    print('Rotate clicked')
                    self.Rotate()

                elif action.text() == 'Delete':
                    print('Delete clicked')
                    self.deleteMe()
                    self.parent().elements.remove(self)

        super(Current_src, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)

            # Moving element to new position
            self.move(newPos)
            if self.direction1 and self.direction0:
                self.nodeP.move(newPos.x() + 45, newPos.y() + 90)
                self.nodeS.move(newPos.x() + 45, newPos.y())
                self.valueText.move(newPos.x() + 90, newPos.y() + 40)
                self.idLabel.move(newPos.x() + 90, newPos.y() + 20)
                self.impedanceText.move(newPos.x() + 90, newPos.y() + 60)
                self.freqText.move(newPos.x() + 90, newPos.y() + 80)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 20,
                                   self.parent().frameGeometry().top() + newPos.y() + 100)
            elif self.direction1 and not self.direction0:
                self.nodeP.move(newPos.x(), newPos.y() + 45)
                self.nodeS.move(newPos.x() + 90, newPos.y() + 45)
                self.valueText.move(newPos.x() + 30, newPos.y() + 90)
                self.idLabel.move(newPos.x() + 45, newPos.y())
                self.impedanceText.move(newPos.x() + 30, newPos.y() + 110)
                self.freqText.move(newPos.x() + 30, newPos.y() + 130)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            elif self.direction0 and not self.direction1:
                self.nodeP.move(newPos.x() + 45, newPos.y())
                self.nodeS.move(newPos.x() + 45, newPos.y() + 90)
                self.valueText.move(newPos.x() + 90, newPos.y() + 40)
                self.idLabel.move(newPos.x() + 90, newPos.y() + 20)
                self.impedanceText.move(newPos.x() + 90, newPos.y() + 60)
                self.freqText.move(newPos.x() + 90, newPos.y() + 80)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            else:
                self.nodeP.move(newPos.x() + 90, newPos.y() + 45)
                self.nodeS.move(newPos.x(), newPos.y() + 45)
                self.valueText.move(newPos.x() + 30, newPos.y() + 90)
                self.idLabel.move(newPos.x() + 45, newPos.y())
                self.impedanceText.move(newPos.x() + 30, newPos.y() + 110)
                self.freqText.move(newPos.x() + 30, newPos.y() + 130)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            self.__mouseMovePos = globalPos
        super(Current_src, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super(Current_src, self).mouseReleaseEvent(event)

    def Rotate(self):
        if self.direction1 and self.direction0:
            self.symbol = QPixmap()
            self.symbol.load('current_src_right.png')
            self.symbol = self.symbol.scaledToHeight(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 30, self.y() + 90)
            self.idLabel.move(self.x() + 45, self.y())
            self.valueText.setText(str(self.value) + '  A')
            self.impedanceText.move(self.x() + 30, self.y() + 110)
            self.impedanceText.setText(str(self.Impedance) + '  ohm')
            self.freqText.move(self.x() + 30, self.y() + 130)
            self.freqText.setText(str(Current_src.freq)+ '  HZ')

            self.nodeP.move(self.x(), self.y() + 45)
            self.nodeS.move(self.x() + 90, self.y() + 45)

            self.direction0 = False
            self.direction1 = True

        elif self.direction1 and not self.direction0:

            self.symbol = QPixmap()
            self.symbol.load('current_src_down.png')
            self.symbol = self.symbol.scaledToWidth(100)
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 90, self.y() + 40)
            self.idLabel.move(self.x() + 90, self.y() + 20)
            self.valueText.setText(str(self.value) +'  A')
            self.impedanceText.move(self.x() + 90, self.y() + 60)
            self.impedanceText.setText(str(self.Impedance) + '  ohm')
            self.freqText.move(self.x() + 90, self.y() + 80)
            self.freqText.setText(str(Current_src.freq) + '  Hz')

            self.nodeP.move(self.x() + 45, self.y())
            self.nodeS.move(self.x() + 45, self.y() + 90)

            self.direction0 = True
            self.direction1 = False

        elif self.direction0 and not self.direction1:
            self.symbol = QPixmap()
            self.symbol.load('current_src_left.png')
            self.symbol = self.symbol.scaledToHeight(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 30, self.y() + 90)
            self.idLabel.move(self.x() + 45, self.y())
            self.valueText.setText(str(self.value)+ '  A')
            self.impedanceText.move(self.x() + 30, self.y() + 110)
            self.impedanceText.setText(str(self.Impedance) + '  ohm')
            self.freqText.move(self.x() + 30, self.y() + 130)
            self.freqText.setText(str(Current_src.freq) + '  Hz')

            self.nodeP.move(self.x() + 90, self.y() + 45)
            self.nodeS.move(self.x(), self.y() + 45)

            self.direction0 = False
            self.direction1 = False

        else:
            self.symbol = QPixmap()
            self.symbol.load('current_src.png')
            self.symbol = self.symbol.scaledToWidth(100)
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 90, self.y() + 40)
            self.idLabel.move(self.x() + 90, self.y() + 20)
            self.valueText.setText(str(self.value)+ '  A')
            self.impedanceText.move(self.x() + 90, self.y() + 60)
            self.impedanceText.setText(str(self.Impedance) + '  ohm')
            self.freqText.move(self.x() + 90, self.y() + 80)
            self.freqText.setText(str(Current_src.freq) + '  Hz')

            self.nodeP.move(self.x() + 45, self.y() + 90)
            self.nodeS.move(self.x() + 45, self.y())

            self.direction0 = True
            self.direction1 = True

    def deleteMe(self):
        self.hide()
        self.nodeP.hide()
        self.nodeS.hide()
        self.idLabel.hide()
        self.valueText.hide()
        self.impedanceText.hide()
        self.freqText.hide()

    def show_detail(self):
        self.setStyleSheet('background-color: yellow')

    def hide_detail(self):
        self.setStyleSheet('background-color: none')



## Resistor class --------------------------------------------

class Resistor(element):
    def __init__(self, name, parent, value = 1000):
        element.__init__(self, name, parent, value)
        self.Impedance = self.value

        # adding image to resistor(that is a QLabel object itself) as its symbol
        self.symbol = QPixmap()
        self.symbol.load('res.png')
        self.symbol = self.symbol.scaledToWidth(100)
        self.resize(self.symbol.size())
        self.setPixmap(self.symbol)
        self.move(100, 100)

        self.valueText = QLineEdit(parent)
        self.valueText.move(self.x() + 25, self.y() + 70)
        self.valueText.resize(70, 15)
        self.valueText.setText(str(self.Impedance) + '  ohm')

        self.idLabel = QLabel(parent)
        self.idLabel.move(self.x() + 50, self.y() + 15)
        self.idLabel.resize(20, 15)
        self.idLabel.setText(str(self.name))
        self.idLabel.show()

        self.nodeP = node(parent)
        self.nodeS = node(parent)
        self.nodeP.move(self.x(), self.y() + 45)
        self.nodeS.move(self.x() + 90, self.y() + 45)
        self.nodeP.show()
        self.nodeS.show()
        # first element tahr is connected to a ned is It's element.
        self.nodeP.connected_elements.add(self.name)
        self.nodeS.connected_elements.add(self.name)

        # When right click on element a menu pops on
        self.PropMenu = QMenu(parent)
        self.PropMenu.addAction('Change Value')
        self.PropMenu.addAction('Rotate')
        self.PropMenu.addAction('Delete')
        # Setting Geometry of menu
        self.PropMenu.move(parent.frameGeometry().left() + self.x() + 20,
                           parent.frameGeometry().top() + self.y() + 100)

        self.isHorizontal = True

        self.direction_label = QLabel(parent)
        self.direction = QPixmap()

        self.valueText.show()
        self.show()

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        if event.button() == QtCore.Qt.RightButton:
            action = self.PropMenu.exec()

            if action is not None:
                if action.text() == 'Change Value':
                    print('Change Value clicked')
                    self.value = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())
                    self.Impedance = self.value

                elif action.text() == 'Rotate':
                    print('Rotate clicked')
                    self.Rotate()

                elif action.text() == 'Delete':
                    print('Delete clicked')
                    self.deleteMe()
                    self.parent().elements.remove(self)

        super(Resistor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)

            # Moving element to new position
            self.move(newPos)
            if self.isHorizontal:
                self.nodeP.move(newPos.x(), newPos.y() + 45)
                self.nodeS.move(newPos.x() + 90, newPos.y() + 45)
                self.valueText.move(newPos.x() + 25, newPos.y() + 70)
                self.idLabel.move(newPos.x() + 50, newPos.y() + 15)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 20,
                                   self.parent().frameGeometry().top() + newPos.y() + 100)

            else:
                self.nodeP.move(newPos.x() + 45, newPos.y())
                self.nodeS.move(newPos.x() + 45, newPos.y() + 90)
                self.valueText.move(newPos.x() + 70, newPos.y() + 45)
                self.idLabel.move(newPos.x() + 70, newPos.y() + 30)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            self.__mouseMovePos = globalPos
        super(Resistor, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(Resistor, self).mouseReleaseEvent(event)

    def Rotate(self):
        if(self.isHorizontal):
            self.symbol = QPixmap()
            self.symbol.load('res3.png')
            self.symbol = self.symbol.scaledToHeight(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 70, self.y() + 45)
            self.idLabel.move(self.x() + 70, self.y() + 30)
            self.valueText.setText(str(self.value) + '  ohm')

            self.nodeP.move(self.x() + 45, self.y())
            self.nodeS.move(self.x() + 45, self.y() + 90)

            self.isHorizontal = False

        else:
            self.symbol = QPixmap()
            self.symbol.load('res.png')
            self.symbol = self.symbol.scaledToWidth(100)
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 25, self.y() + 70)
            self.idLabel.move(self.x() + 50, self.y() + 15)
            self.valueText.setText(str(self.value) + '  ohm')

            self.nodeP.move(self.x(), self.y() + 45)
            self.nodeS.move(self.x() + 90, self.y() + 45)

            self.isHorizontal = True

    def deleteMe(self):
        self.hide()
        self.nodeP.hide()
        self.nodeS.hide()
        self.idLabel.hide()
        self.valueText.hide()

    def show_detail(self):
        self.setStyleSheet("background-color: yellow")
        if self.isHorizontal:
            self.direction.load('arrow_right.png')
            self.direction = self.direction.scaledToWidth(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()
        else:
            self.direction.load('arrow_down.png')
            self.direction = self.direction.scaledToHeight(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()

    def hide_detail(self):
        self.setStyleSheet("background-color: none")
        self.direction_label.hide()



## Capacitor class --------------------------------------------

class Capacitor(element):
    def __init__(self, name, parent, value = 0.000001):
        element.__init__(self, name, parent, value)
        self.Impedance = 1 / (1j * np.pi * Current_src.freq * self.value)


        # adding image to resistor(that is a QLabel object itself) as its symbol
        self.symbol = QPixmap()
        self.symbol.load('cap.png')
        self.symbol = self.symbol.scaledToWidth(100)
        self.resize(self.symbol.size())
        self.setPixmap(self.symbol)
        self.move(100, 200)

        self.valueText = QLineEdit(parent)
        self.valueText.move(self.x() + 35, self.y() + 80)
        self.valueText.resize(50, 15)
        self.valueText.setText(str(self.value) + '  F')

        self.idLabel = QLabel(parent)
        self.idLabel.move(self.x() + 45, self.y())
        self.idLabel.resize(20, 15)
        self.idLabel.setText(str(self.name))
        self.idLabel.show()

        self.nodeP = node(parent)
        self.nodeS = node(parent)
        self.nodeP.move(self.x(), self.y() + 40)
        self.nodeS.move(self.x() + 90, self.y() + 40)
        self.nodeP.show()
        self.nodeS.show()
        # first element tahr is connected to a ned is It's element.
        self.nodeP.connected_elements.add(self.name)
        self.nodeS.connected_elements.add(self.name)

        # When right click on element a menu pops on
        self.PropMenu = QMenu(parent)
        self.PropMenu.addAction('Change Value')
        self.PropMenu.addAction('Rotate')
        self.PropMenu.addAction('Delete')
        # Setting Geometry of menu
        self.PropMenu.move(parent.frameGeometry().left() + self.x() + 20,
                           parent.frameGeometry().top() + self.y() + 100)

        self.isHorizontal = True

        self.direction_label = QLabel(parent)
        self.direction = QPixmap()

        self.valueText.show()
        self.show()

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        if event.button() == QtCore.Qt.RightButton:
            action = self.PropMenu.exec()

            if action is not None:
                if action.text() == 'Change Value':
                    print('Change Value clicked')
                    self.value = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())
                    self.Impedance = 1 / (1j * np.pi * Current_src.freq * self.value)

                elif action.text() == 'Rotate':
                    print('Rotate clicked')
                    self.Rotate()

                elif action.text() == 'Delete':
                    print('Delete clicked')
                    self.deleteMe()
                    self.parent().elements.remove(self)

        super(Capacitor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)

            # Moving element to new position
            self.move(newPos)
            if self.isHorizontal:
                self.nodeP.move(newPos.x(), newPos.y() + 40)
                self.nodeS.move(newPos.x() + 90, newPos.y() + 40)
                self.valueText.move(newPos.x() + 35, newPos.y() + 80)
                self.idLabel.move(newPos.x() + 45, newPos.y())
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 20,
                                   self.parent().frameGeometry().top() + newPos.y() + 100)

            else:
                self.nodeP.move(newPos.x() + 40, newPos.y())
                self.nodeS.move(newPos.x() + 40, newPos.y() + 90)
                self.valueText.move(newPos.x() + 80, newPos.y() + 45)
                self.idLabel.move(newPos.x() + 80, newPos.y() + 25)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            self.__mouseMovePos = globalPos
        super(Capacitor, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(Capacitor, self).mouseReleaseEvent(event)

    def Rotate(self):
        if(self.isHorizontal):
            self.symbol = QPixmap()
            self.symbol.load('cap2.png')
            self.symbol = self.symbol.scaledToHeight(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 80, self.y() + 45)
            self.idLabel.move(self.x() + 80, self.y() + 25)
            self.valueText.setText(str(self.value) + '  F')

            self.nodeP.move(self.x() + 40, self.y())
            self.nodeS.move(self.x() + 40, self.y() + 90)

            self.isHorizontal = False

        else:
            self.symbol = QPixmap()
            self.symbol.load('cap.png')
            self.symbol = self.symbol.scaledToWidth(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 25, self.y() + 80)
            self.idLabel.move(self.x() + 45, self.y())
            self.valueText.setText(str(self.value) + '  F')

            self.nodeP.move(self.x(), self.y() + 40)
            self.nodeS.move(self.x() + 90, self.y() + 40)

            self.isHorizontal = True

    def deleteMe(self):
        self.hide()
        self.nodeP.hide()
        self.nodeS.hide()
        self.idLabel.hide()
        self.valueText.hide()

    def show_detail(self):
        self.setStyleSheet("background-color: yellow")
        if self.isHorizontal:
            self.direction.load('arrow_right.png')
            self.direction = self.direction.scaledToWidth(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()
        else:
            self.direction.load('arrow_down.png')
            self.direction = self.direction.scaledToHeight(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()

    def hide_detail(self):
        self.setStyleSheet("background-color: none")
        self.direction_label.hide()

## Inductor class --------------------------------------------

class Inductor(element):
    def __init__(self, name, parent, value = 0.01):
        element.__init__(self, name, parent, value)
        self.Impedance = 1j *2 * np.pi * Current_src.freq * self.value

        # adding image to resistor(that is a QLabel object itself) as its symbol
        self.symbol = QPixmap()
        self.symbol.load('ind.png')
        self.symbol = self.symbol.scaledToWidth(100)
        self.resize(self.symbol.size())
        self.setPixmap(self.symbol)
        self.move(200, 100)

        self.valueText = QLineEdit(parent)
        self.valueText.move(self.x() + 30, self.y() + 40)
        self.valueText.resize(50, 15)
        self.valueText.setText(str(self.value) + '  H')

        self.idLabel = QLabel(parent)
        self.idLabel.move(self.x() + 45, self.y())
        self.idLabel.resize(20, 15)
        self.idLabel.setText(str(self.name))
        self.idLabel.show()

        self.nodeP = node(parent)
        self.nodeS = node(parent)
        self.nodeP.move(self.x(), self.y() + 22)
        self.nodeS.move(self.x() + 90, self.y() + 22)
        self.nodeP.show()
        self.nodeS.show()
        # first element tahr is connected to a ned is It's element.
        self.nodeP.connected_elements.add(self.name)
        self.nodeS.connected_elements.add(self.name)

        # When right click on element a menu pops on
        self.PropMenu = QMenu(parent)
        self.PropMenu.addAction('Change Value')
        self.PropMenu.addAction('Rotate')
        self.PropMenu.addAction('Delete')
        # Setting Geometry of menu
        self.PropMenu.move(parent.frameGeometry().left() + self.x() + 20,
                           parent.frameGeometry().top() + self.y() + 100)

        self.isHorizontal = True

        self.direction_label = QLabel(parent)
        self.direction = QPixmap()

        self.valueText.show()
        self.show()

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        if event.button() == QtCore.Qt.RightButton:
            action = self.PropMenu.exec()

            if action is not None:
                if action.text() == 'Change Value':
                    print('Change Value clicked')
                    self.value = float(re.match('\d*(?:.\d*e?-?\d*)?', self.valueText.text()).group())
                    self.Impedance = 1j *2 * np.pi * Current_src.freq * self.value

                elif action.text() == 'Rotate':
                    print('Rotate clicked')
                    self.Rotate()

                elif action.text() == 'Delete':
                    print('Delete clicked')
                    self.deleteMe()
                    self.parent().elements.remove(self)

        super(Inductor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)

            # Moving element to new position
            self.move(newPos)
            if self.isHorizontal:
                self.nodeP.move(newPos.x(), newPos.y() + 22)
                self.nodeS.move(newPos.x() + 90, newPos.y() + 22)
                self.valueText.move(newPos.x() + 30, newPos.y() + 40)
                self.idLabel.move(newPos.x() + 45, newPos.y())
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 20,
                                   self.parent().frameGeometry().top() + newPos.y() + 100)
            else:
                self.nodeP.move(newPos.x() + 18, newPos.y())
                self.nodeS.move(newPos.x() + 18, newPos.y() + 90)
                self.valueText.move(newPos.x() + 40, newPos.y() + 45)
                self.idLabel.move(newPos.x() + 40, newPos.y() + 25)
                self.PropMenu.move(self.parent().frameGeometry().left() + newPos.x() + 100,
                                   self.parent().frameGeometry().top() + newPos.y() + 20)

            self.__mouseMovePos = globalPos
        super(Inductor, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(Inductor, self).mouseReleaseEvent(event)

    def Rotate(self):
        if(self.isHorizontal):
            self.symbol = QPixmap()
            self.symbol.load('ind2.png')
            self.symbol = self.symbol.scaledToHeight(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 40, self.y() + 45)
            self.idLabel.move(self.x() + 40, self.y() + 25)
            self.valueText.setText(str(self.value) + ' H')

            self.nodeP.move(self.x() + 18, self.y())
            self.nodeS.move(self.x() + 18, self.y() + 90)

            self.isHorizontal = False

        else:
            self.symbol = QPixmap()
            self.symbol.load('ind.png')
            self.symbol = self.symbol.scaledToWidth(100)
            self.resize(self.symbol.size())
            self.setPixmap(self.symbol)

            self.valueText.move(self.x() + 30, self.y() + 40)
            self.idLabel.move(self.x() + 45, self.y())
            self.valueText.setText(str(self.value) + ' H')

            self.nodeP.move(self.x(), self.y() + 22)
            self.nodeS.move(self.x() + 90, self.y() + 22)

            self.isHorizontal = True

    def deleteMe(self):
        self.hide()
        self.nodeP.hide()
        self.nodeS.hide()
        self.idLabel.hide()
        self.valueText.hide()

    def show_detail(self):
        self.setStyleSheet("background-color: yellow")
        if self.isHorizontal:
            self.direction.load('arrow_right.png')
            self.direction = self.direction.scaledToWidth(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()
        else:
            self.direction.load('arrow_down.png')
            self.direction = self.direction.scaledToHeight(100)
            self.direction_label.resize(self.direction.size())
            self.direction_label.setPixmap(self.direction)
            self.direction_label.move(self.x(), self.y())
            self.direction_label.show()

    def hide_detail(self):
        self.setStyleSheet("background-color: none")
        self.direction_label.hide()