import sys

from PyQt5.QtCore import QFile, QIODevice, QTextStream, Qt, QSize, qrand, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QIcon, QColor
from PyQt5.QtWidgets import *
import urllib.request
import random
import pickle
from pathlib import Path
from datetime import datetime


class myHisto:

    def __init__(self):
        self.m_list = []

    def max(self):
        
        bin_max = 0
        for i in self.m_list:
            if i.m_amount > bin_max:
                bin_max = i.m_amount
        return bin_max

    def total(self):
        total = 0
        for rect in self.m_list:
            total += rect.m_amount

        return total

class Intervalle:

    def __init__(self, a=0, b=0):
        self.m_x = a
        self.m_amount = b


class MyMainWindow(QMainWindow):
    doPaint = False
    doBar = True
    doPie = False

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        # Attributs de la fenetre principale
        self.main_width = 600
        self.main_height = 450
        self.setGeometry(300, 300, self.main_width, self.main_height)
        self.setMinimumSize(QSize(400, 200))
        self.titleInfo = "Histogram application"
        self.titleMainWindow = self.titleInfo + datetime.now().strftime("  %H:%M:%S") + '| Res: ' + str(self.width()) + 'x' + str(self.height())
        self.setWindowTitle(self.titleMainWindow)

        self.setStyleSheet("background-color: white; color: black")

        # Barre de status pour afficher les infos
        self.setAcceptDrops(True)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Creation d'une instance de la classe myHisto
        self.mHisto = myHisto()

        self.colorIcon = QColor(255, 0, 0)
        self.menuBar().setNativeMenuBar(False)
        self.statusBar.showMessage("Zone d'informations, peut toujours servir")
        self.createActions()
        self.createMenus()

    def resizeEvent(self, event):
        self.titleMainWindow = self.titleInfo + datetime.now().strftime("  %H:%M:%S") + '| Res: ' + str(self.width()) + 'x' + str(self.height())
        self.setWindowTitle(self.titleMainWindow)

    def createActions(self):

        # File menu actions
        self.openAct = QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        self.saveAct = QAction("&Save", self)
        self.saveAct.setShortcut("Ctrl+S")
        self.restoreAct = QAction("&Restore", self)
        self.restoreAct.setShortcut("Ctrl+R")
        self.byeAct = QAction("&Bye", self)
        self.byeAct.setShortcut("Ctrl+B")

        # Display menu actions
        self.clearAct = QAction("&Clear", self)
        self.clearAct.setShortcut("Ctrl+C")
        self.colorAct = QAction("&Color", self)
        self.colorAct.setShortcut("Ctrl+V")
        color_icon = QPixmap(10, 10)
        color_icon.fill(self.colorIcon)
        self.colorAct.setIcon(QIcon(color_icon))

        # Draw menu action
        self.barAct = QAction("&Bar", self)
        self.barAct.setShortcut("Ctrl+M")
        self.pieAct = QAction("&Pie", self)
        self.pieAct.setShortcut("Ctrl+P")

        # Assigning slots to QAction items
        self.openAct.triggered.connect(self.clickedOpen)
        self.saveAct.triggered.connect(self.clickedSave)
        self.restoreAct.triggered.connect(self.clickedRestore)
        self.byeAct.triggered.connect(self.clickedBye)
        self.clearAct.triggered.connect(self.clickedClear)
        self.colorAct.triggered.connect(self.clickedColor)
        self.barAct.triggered.connect(self.clickedBar)
        self.pieAct.triggered.connect(self.clickedPie)

    def createMenus(self):
        # File menus
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addAction(self.restoreAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.byeAct)

        # Display menus
        displayMenu = self.menuBar().addMenu("&Display")
        displayMenu.addAction(self.clearAct)
        displayMenu.addAction(self.colorAct)

        # Draw menu
        drawMenu = self.menuBar().addMenu("&Draw")
        drawMenu.addAction(self.barAct)
        drawMenu.addAction(self.pieAct)

    def clickedOpen(self):
        self.statusBar.showMessage("Histogram opened !")
        filename, txt = QFileDialog.getOpenFileName(self, "Open a file", "./", "Data files (*.dat)")
        if filename:
            file = QFile(filename)
            file.open(QIODevice.ReadOnly)
            self.mHisto.m_list.clear()
            index = 0
            for val in QTextStream(file).readAll().split("\n"):
                self.mHisto.m_list.append(Intervalle(index, int(val)))
                index += 1
            self.doPaint = True
            self.repaint()

    def clickedSave(self):
        filename = "saveHisto.bin"
        with open(filename, 'w+b') as pickle_file:
            pickle.dump(self.mHisto.m_list, pickle_file)
        self.statusBar.showMessage("Histogram saved !")

    def clickedRestore(self):
        filename = "saveHisto.bin"
        file = Path(filename)
        if file.is_file():
            with open(filename, 'rb') as pickle_file:
                self.mHisto.m_list = pickle.load(pickle_file)
            self.doPaint = True
            self.repaint()
        self.statusBar.showMessage("Histogram restored !")

    def clickedBye(self):
        self.statusBar.showMessage("Histogram said bye !")
        QApplication.instance().quit()

    def clickedClear(self):
        self.doPaint = False
        self.repaint()
        self.statusBar.showMessage("Histogram cleared !")

    def clickedColor(self):
        selected_color = QColorDialog.getColor()
        if selected_color.isValid():
            self.colorIcon = selected_color.toRgb()
            color_icon = QPixmap(10, 10)
            color_icon.fill(self.colorIcon)
            self.colorAct.setIcon(QIcon(color_icon))
            self.repaint()
        self.statusBar.showMessage("Histogram colored !")

    def clickedBar(self):
        self.doPie = False
        self.doBar = True
        self.repaint()
        self.statusBar.showMessage("Invoked draw bar !")

    def clickedPie(self):
        self.doPie = True
        self.doBar = False
        self.main_width, self.main_height = 500, 500
        self.setGeometry(300, 300, self.main_width, self.main_height)
        self.repaint()
        self.statusBar.showMessage("Invoked draw pie !")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename_drop = url.toLocalFile()
            self.statusBar.showMessage("File: " + filename_drop)
            file_drop = QFile(filename_drop)
            file_drop.open(QIODevice.ReadOnly)
            self.mHisto.m_list.clear()
            index = 0
            for val in QTextStream(file_drop).readAll().split("\n"):
                self.mHisto.m_list.append(Intervalle(index, int(val)))
                index += 1
            self.doPaint = True
            self.repaint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.mHisto.m_list.clear()
            for x in range(0, 10):
                val = random.randint(0, 99)
                self.mHisto.m_list.append(Intervalle(x, val))
            self.doPaint = True
            self.repaint()
            self.statusBar.showMessage("Random histogram created!")

    def paintEvent(self, event):
        self.main_width = self.width()
        self.main_height = self.height()

        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(self.colorIcon, Qt.SolidPattern))
        # Painting start
        if self.doPaint:
            if self.doBar:
                max_val = self.mHisto.max()
                segment = int(self.main_width / len(self.mHisto.m_list))
                rescale = self.main_height / max_val
                x = 0
                for rect in self.mHisto.m_list:
                    height = rect.m_amount * rescale
                    y = self.main_height - height
                    painter.drawRect(int(x), int(y), int(segment), int(height))
                    x += segment
            elif self.doPie:
                angle_scale = 360/self.mHisto.total()
                start_angle = 0
                segment = QRect(0, 0, 400, 400)
                for rect in self.mHisto.m_list:
                    painter.setBrush(QColor(qrand()%256, qrand()%256, qrand()%256))
                    centre = QPoint(int(self.width()/2), int(self.width()/2))
                    segment.moveCenter(centre)
                    span_angle = (rect.m_amount * angle_scale) * 16
                    painter.drawPie(segment, int(start_angle), int(span_angle))
                    start_angle += span_angle

        # Painting end
        painter.end()

    def myExit(self):
        self.statusBar.showMessage("Quit ...")
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    sys.exit(app.exec_())
