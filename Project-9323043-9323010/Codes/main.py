from elements import *
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
import os
import numpy as np

Form = uic.loadUiType(os.path.join(os.getcwd(), 'gui.ui'))[0]
Form2 = uic.loadUiType(os.path.join(os.getcwd(), 'gui2.ui'))[0]

class circuit_gui(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.nodes2beConnected = []
        self.wireEnable = False
        self.wire_Button.clicked.connect(self.add_wire)

        self.elements = []

        self.resistor_dict = {} #Defining a dictionary for resistors
        self.node_dict = {}
        self.node_dict['N0'] = set([])
        self.resistor_number = 0

        self.capacitor_dict = {}  # Defining a dictionary for capacitors
        self.capacitor_number = 0

        self.currentSrc_number = 0

        self.inductor_number = 0

        self.node_number = 1
        self.resistor_Button.clicked.connect(self.add_res)
        self.ground_Button.clicked.connect(self.add_gnd)
        self.capacitor_Button.clicked.connect(self.add_cap)
        self.currentSrc_Button.clicked.connect(self.add_currentSrc)
        self.inductor_Button.clicked.connect(self.add_inductor)
        # Menu bar actions:
        self.actionSimulate.triggered.connect(self.Analyze)

        self.A = None
        self.J_S = None
        self.Yb = None
        self.Y = None
        self.Is = None
        self.e = None
        self.V = None
        self.J = None

        self.nodes = []
        self.branches = []

    def connectNodes(self):
        horizentalWire = QLabel(w)
        horizentalWire.setStyleSheet("background-color:blue")
        verticalWire = QLabel(w)
        verticalWire.setStyleSheet("background-color:blue")

        if self.nodes2beConnected[1].x() - self.nodes2beConnected[0].x() > 0:
            horizentalWire.setGeometry(self.nodes2beConnected[0].x(),
                                       self.nodes2beConnected[0].y(),
                                       abs(self.nodes2beConnected[1].x() - self.nodes2beConnected[0].x()), 2)
            if self.nodes2beConnected[1].y() - self.nodes2beConnected[0].y() > 0:
                verticalWire.setGeometry(
                    horizentalWire.x() + (abs(self.nodes2beConnected[1].x() - self.nodes2beConnected[0].x())),
                    horizentalWire.y(),
                    2, abs(self.nodes2beConnected[0].y() - self.nodes2beConnected[1].y()))
            else:
                verticalWire.setGeometry(self.nodes2beConnected[1].x(),
                                         self.nodes2beConnected[1].y(),
                                         2, abs(self.nodes2beConnected[0].y() - self.nodes2beConnected[1].y()))

        else:
            horizentalWire.setGeometry(self.nodes2beConnected[1].x(),
                                       self.nodes2beConnected[1].y(),
                                       abs(self.nodes2beConnected[1].x() - self.nodes2beConnected[0].x()), 2)
            if self.nodes2beConnected[0].y() - self.nodes2beConnected[1].y() > 0:
                verticalWire.setGeometry(
                    horizentalWire.x() + (abs(self.nodes2beConnected[1].x() - self.nodes2beConnected[0].x())),
                    horizentalWire.y(),
                    2, abs(self.nodes2beConnected[0].y() - self.nodes2beConnected[1].y()))
            else:
                verticalWire.setGeometry(self.nodes2beConnected[0].x(),
                                         self.nodes2beConnected[0].y(),
                                         2, abs(self.nodes2beConnected[0].y() - self.nodes2beConnected[1].y()))

        horizentalWire.show()
        verticalWire.show()
        print("Nodes are connected")


    def add_currentSrc(self):
        temp = Current_src('I%i'%self.currentSrc_number, w)
        self.elements.append(temp)
        self.currentSrc_number += 1

    def add_inductor(self):
        temp = Inductor('L%i'%self.inductor_number, w)
        self.elements.append(temp)
        self.inductor_number += 1


    def add_res(self):
        temp = Resistor('R%i'%self.resistor_number, w)
        self.elements.append(temp)
        self.resistor_dict['R%i'%self.resistor_number] = temp
        # print(self.resistor_dict['R%i'%self.resistor_number].name)
        self.resistor_number += 1

    def add_cap(self):
        temp = Capacitor('C%i' % self.capacitor_number, w)
        self.elements.append(temp)
        self.capacitor_dict['C%i' % self.capacitor_number] = temp
        print(self.capacitor_dict['C%i' % self.capacitor_number].name)
        self.capacitor_number += 1

    def add_gnd(self):
        Ground(w)

    def add_wire(self):
        self.wireEnable = True

    def Analyze(self):
        row = 0
        column = 0
        self.A = np.zeros((self.node_dict.__len__() - 1, self.elements.__len__()))
        for N in self.node_dict.keys():
            if N == 'N0':
                continue
            NodeInSet = self.node_dict[N].pop()
            self.node_dict[N].add(NodeInSet)
            self.nodes.append(N)
            for elem in self.elements:
                self.branches.append(elem.name)
                if elem.name in NodeInSet.connected_elements:
                    if elem.nodeP.id == N:
                        # print("nodeP check")
                        self.A[row][column] = 1

                    elif elem.nodeS.id == N:
                        # print("nodeS check")
                        self.A[row][column] = -1
                else:
                    # print("else")
                    self.A[row][column] = 0
                column += 1
            column = 0
            row += 1
        print("\nA = {}".format(self.A))

        self.J_S = np.zeros((self.elements.__len__(), 1))
        i = 0
        for elem in self.elements:
            if elem.name[0] == 'I':
                self.J_S[i] = elem.value
            i += 1
        print("\nJ_S = {}".format(self.J_S))

        self.Yb = np.zeros((self.elements.__len__(), self.elements.__len__()), dtype=complex)
        i = 0
        for elem in self.elements:
            print(elem.name)
            self.Yb[i][i] = 1/elem.Impedance
            i += 1
        print("\nYb ={}".format(self.Yb))

        self.Y = np.dot(np.dot(self.A , self.Yb), np.transpose(self.A))
        print("\nY ={}".format(self.Y))
        self.Is = -np.dot(self.A , self.J_S)
        print("\n IS = {}".format(self.Is))

        # voltage of nodes
        self.e = np.dot(np.linalg.inv(self.Y), self.Is)
        print("e = {}".format(self.e))
        #voltage of branches
        self.V = np.dot(np.transpose(self.A) , self.e)
        print("V = {}".format(self.V))
        #current of branches
        self.J = np.dot(self.Yb , self.V )+ self.J_S
        print("J ={}".format(self.J))

        w2.update_variables()

        w2.show()







class result_gui(QWidget, Form2):
    def __init__(self, parent):
        Form2.__init__(self)
        QWidget.__init__(self)
        self.setupUi(self)
        self.parent = parent
        self.A = None
        self.J_S = None
        self.Yb = None
        self.Y = None
        self.Is = None
        self.e = None
        self.V = None
        self.J = None
        self.m = None
        self.n = None

        self.matrix = None
        self.labelMatrix_row = []
        self.labelMatrix_column = []

        self.state = None

        self.A_Button.clicked.connect(self.show_A)
        self.Js_Button.clicked.connect(self.show_Js)
        self.Yb_Button.clicked.connect(self.show_Yb)
        self.Y_Button.clicked.connect(self.show_Y)
        self.Is_Button.clicked.connect(self.show_Is)
        self.e_Button.clicked.connect(self.show_e)
        self.V_Button.clicked.connect(self.show_V)
        self.J_Button.clicked.connect(self.show_J)


    def update_variables(self):
        self.A = self.parent.A
        self.J_S = self.parent.J_S
        self.Yb = self.parent.Yb
        self.Y = self.parent.Y
        self.Is = self.parent.Is
        self.e = self.parent.e
        self.V = self.parent.V
        self.J = self.parent.J

    def show_A(self):
        self.clear()
        x = 30
        y = 30
        (self.m,self.n) = np.shape(self.A)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str(self.A[i][j]))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 30
        y = 10
        for i in range(self.n):
            self.labelMatrix_row.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_row[i].setGeometry(x, y, 60, 15)
            self.labelMatrix_row[i].setText(str(self.parent.branches[i]))
            self.labelMatrix_row[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_row[i].show()
            x += 70

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.nodes[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'A'


    def show_Js(self):
       self.clear()
       x = 30
       y = 30
       (self.m, self.n) = np.shape(self.J_S)
       self.matrix = []
       for i in range(self.m):
           self.matrix.append([])
           for j in range(self.n):
               self.matrix[i].append(QLabel(parent=self.matrix_widget))
               self.matrix[i][j].setGeometry(x, y, 60, 60)
               x += 70
               self.matrix[i][j].setText(str(self.J_S[i][j]))
               self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
               self.matrix[i][j].show()
           y += 70
           x = 30

       x = 10
       y = 30
       for i in range(self.m):
           self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
           self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
           self.labelMatrix_column[i].setText(str(self.parent.branches[i]))
           self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
           self.labelMatrix_column[i].show()
           y += 70

       self.state = 'J_S'


    def show_Yb(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.Yb)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str('{:.4f}'.format(self.Yb[i][j].real))+
                                          '\nj'+
                                          str('{:.4f}'.format(self.Yb[i][j].imag)))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 30
        y = 10
        for i in range(self.n):
            self.labelMatrix_row.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_row[i].setGeometry(x, y, 60, 15)
            self.labelMatrix_row[i].setText(str(self.parent.branches[i]))
            self.labelMatrix_row[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_row[i].show()
            x += 70

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.branches[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'Yb'

    def show_Y(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.Y)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str('{:.4f}'.format(self.Y[i][j].real)) +
                                          '\nj' +
                                          str('{:.4f}'.format(self.Y[i][j].imag)))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 30
        y = 10
        for i in range(self.n):
            self.labelMatrix_row.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_row[i].setGeometry(x, y, 60, 15)
            self.labelMatrix_row[i].setText(str(self.parent.nodes[i]))
            self.labelMatrix_row[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_row[i].show()
            x += 70

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.nodes[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'Y'

    def show_Is(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.Is)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str(self.Is[i][j]))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        self.state = 'Is'

    def show_e(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.e)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str('{:.4f}'.format(self.e[i][j].real)) +
                                          '\nj' +
                                          str('{:.4f}'.format(self.e[i][j].imag)))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.nodes[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'e'

    def show_V(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.V)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent=self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str('{:.4f}'.format(self.V[i][j].real)) +
                                          '\nj' +
                                          str('{:.4f}'.format(self.V[i][j].imag)))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.branches[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'V'

    def show_J(self):
        self.clear()
        x = 30
        y = 30
        (self.m, self.n) = np.shape(self.J)
        self.matrix = []
        for i in range(self.m):
            self.matrix.append([])
            for j in range(self.n):
                self.matrix[i].append(QLabel(parent = self.matrix_widget))
                self.matrix[i][j].setGeometry(x, y, 60, 60)
                x += 70
                self.matrix[i][j].setText(str('{:.4f}'.format(self.J[i][j].real)) +
                                          '\nj' +
                                          str('{:.4f}'.format(self.J[i][j].imag)))
                self.matrix[i][j].setStyleSheet("background-color:wheat; qproperty-alignment: AlignCenter;")
                self.matrix[i][j].show()
            y += 70
            x = 30

        x = 10
        y = 30
        for i in range(self.m):
            self.labelMatrix_column.append(QLabel(parent=self.matrix_widget))
            self.labelMatrix_column[i].setGeometry(x, y, 15, 60)
            self.labelMatrix_column[i].setText(str(self.parent.branches[i]))
            self.labelMatrix_column[i].setStyleSheet("qproperty-alignment: AlignCenter;")
            self.labelMatrix_column[i].show()
            y += 70

        self.state = 'J'

    def clear(self):
        if self.matrix is not None:
            for i in range(self.m):
                row = self.matrix.pop()
                for j in range(self.n):
                    row.pop().hide()
        if self.labelMatrix_row.__len__() > 0:
            for i in range(self.n):
                self.labelMatrix_row.pop().hide()
        if self.labelMatrix_column.__len__() > 0:
            for i in range(self.m):
                self.labelMatrix_column.pop().hide()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            row = int((event.pos().y() - 30) / 70)
            column = int((event.pos().x() - 30) / 70)
            for i in range(self.m):
                for j in range(self.n):
                    if i == row and j == column:
                        self.matrix[row][column].setStyleSheet("background : blue")
                    else:
                        self.matrix[i][j].setStyleSheet("background : wheat")

            if self.state == 'A':
                if row < self.parent.nodes.__len__() and column < self.parent.branches.__len__():
                    for elem in self.parent.elements:
                        if elem.name == self.parent.branches[column]:
                            elem.show_detail()
                        else:
                            elem.hide_detail()

                    for node_id in self.parent.node_dict.keys():
                        if node_id == self.parent.nodes[row]:
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:red")
                        else:
                            if node_id is not 'N0':
                                for NODE in self.parent.node_dict[node_id]:
                                    NODE.setStyleSheet("background-color:blue")
                else:
                    for elem in self.parent.elements:
                        elem.hide_detail()

                    for node_id in self.parent.node_dict.keys():
                        if node_id is not 'N0':
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:blue")

            elif self.state == 'J_S':
                if row < self.parent.branches.__len__() and column == 0:
                    for elem in self.parent.elements:
                        if elem.name == self.parent.branches[row]:
                            elem.show_detail()
                        else:
                            elem.hide_detail()
                else:
                    for elem in self.parent.elements:
                        elem.hide_detail()

            elif self.state == 'Yb':
                if row < self.parent.branches.__len__() and column < self.parent.branches.__len__() and row == column:
                    for elem in self.parent.elements:
                        if elem.name == self.parent.branches[column]:
                            elem.show_detail()
                        else:
                            elem.hide_detail()
                else:
                    for elem in self.parent.elements:
                        elem.hide_detail()

            elif self.state == 'Y':
                if row < self.parent.nodes.__len__() and column < self.parent.nodes.__len__():
                    for node_id in self.parent.node_dict.keys():
                        if node_id == self.parent.nodes[row] or node_id == self.parent.nodes[column]:
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:red")
                        else:
                            if node_id is not 'N0':
                                for NODE in self.parent.node_dict[node_id]:
                                    NODE.setStyleSheet("background-color:blue")
                else:
                    for node_id in self.parent.node_dict.keys():
                        if node_id is not 'N0':
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:blue")

            elif self.state == 'Is':
                pass

            elif self.state == 'e':
                if row < self.parent.nodes.__len__() and column == 0:
                    for node_id in self.parent.node_dict.keys():
                        if node_id == self.parent.nodes[row]:
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:red")
                        else:
                            if node_id is not 'N0':
                                for NODE in self.parent.node_dict[node_id]:
                                    NODE.setStyleSheet("background-color:blue")
                else:
                    for node_id in self.parent.node_dict.keys():
                        if node_id is not 'N0':
                            for NODE in self.parent.node_dict[node_id]:
                                NODE.setStyleSheet("background-color:blue")

            elif self.state == 'V':
                if row < self.parent.branches.__len__() and column == 0:
                    for elem in self.parent.elements:
                        if elem.name == self.parent.branches[row]:
                            elem.show_detail()
                        else:
                            elem.hide_detail()
                else:
                    for elem in self.parent.elements:
                        elem.hide_detail()

            elif self.state == 'J':
                if row < self.parent.branches.__len__() and column == 0:
                    for elem in self.parent.elements:
                        if elem.name == self.parent.branches[row]:
                            elem.show_detail()
                        else:
                            elem.hide_detail()
                else:
                    for elem in self.parent.elements:
                        elem.hide_detail()





app = QApplication(sys.argv)
w = circuit_gui()
w.show()
w2 = result_gui(w)

sys.exit(app.exec())