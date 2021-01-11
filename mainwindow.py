# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
import os
import sheet
import cv2

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(909, 752)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.numImgLabel = QtWidgets.QLabel(self.centralwidget)
        self.numImgLabel.setGeometry(QtCore.QRect(30, 30, 300, 200))
        self.numImgLabel.setObjectName("numImgLabel")
        self.ansImgLabel = QtWidgets.QLabel(self.centralwidget)
        self.ansImgLabel.setGeometry(QtCore.QRect(20, 280, 600, 400))
        self.ansImgLabel.setObjectName("ansImgLabel")
        self.courseImgLabel = QtWidgets.QLabel(self.centralwidget)
        self.courseImgLabel.setGeometry(QtCore.QRect(710, 280, 150, 400))
        self.courseImgLabel.setObjectName("courseImgLabel")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(450, 20, 421, 201))
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 909, 23))
        self.menubar.setObjectName("menubar")
        self.menuFIle = QtWidgets.QMenu(self.menubar)
        self.menuFIle.setObjectName("menuFIle")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_scan = QtWidgets.QAction(MainWindow)
        self.action_scan.setObjectName("action_scan")
        self.action_in = QtWidgets.QAction(MainWindow)
        self.action_in.setObjectName("action_in")
        self.action_check = QtWidgets.QAction(MainWindow)
        self.action_check.setObjectName("action_check")
        self.menuFIle.addAction(self.action_scan)
        self.menuFIle.addAction(self.action_in)
        self.menuFIle.addAction(self.action_check)
        self.menubar.addAction(self.menuFIle.menuAction())

        # 变量
        self.ans=[]
        self.checkState=[]
        self.correctNum=0
        self.NO="Nan"
        self.course="Nan"
        self.IDAnswer=[]
        # 连接槽
        self.action_scan.triggered.connect(self.selectImg)
        self.action_in.triggered.connect(self.readAns)
        self.action_check.triggered.connect(self.check)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.numImgLabel.setText(_translate("MainWindow", "学号"))
        self.ansImgLabel.setText(_translate("MainWindow", "答题"))
        self.courseImgLabel.setText(_translate("MainWindow", "科目"))
        self.menuFIle.setTitle(_translate("MainWindow", "文件"))
        self.action_scan.setText(_translate("MainWindow", "打开并扫描答题卡"))
        self.action_in.setText(_translate("MainWindow", "导入标准答案"))
        self.action_check.setText(_translate("MainWindow", "校对答案"))

    def flash(self):
        self.checkState=['N' for i in range(len(self.ans)+1)]
        self.correctNum=0

    def selectImg(self):
        fileName,fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选取文件", os.getcwd(), 
        "Image Files(*.jpg)")
        print("select"+fileName)
        if(fileName==''):
            return
        self.flash()
        (numImg,courseImg,ansImg),(NO,course,IDAnswer)=sheet.solve(fileName)
        cv2.imwrite("numImg.jpg",numImg)
        cv2.imwrite("courseImg.jpg",courseImg)
        cv2.imwrite("ansImg.jpg",ansImg)
        self.NO=NO
        self.course=course
        self.IDAnswer=IDAnswer
        pix=QPixmap("numImg.jpg")
        self.numImgLabel.setPixmap(pix)
        pix=QPixmap("courseImg.jpg")
        self.courseImgLabel.setPixmap(pix)
        pix=QPixmap("ansImg.jpg")
        self.ansImgLabel.setPixmap(pix)

    def readAns(self):
        fileName,fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选取文件", os.getcwd(), 
        "Text Files(*.txt)")
        print("select"+fileName)
        if(fileName==''):
            return
        with open(fileName) as f:
            self.ans=f.read().split()
        self.flash()

    def check(self):
        for i,a in self.IDAnswer:
            if i<=len(self.ans) and i>0:
                # 一空多填则判断为错
                if a==self.ans[i-1] and self.checkState[i]=='N':
                    self.checkState[i]='T'
                else:
                    self.checkState[i]='F'

        for s in self.checkState:
            if s=='T':
                self.correctNum+=1
        s=''
        s+="科目：{}\n".format(self.course)
        s+="学号：{}\n".format(self.NO)
        s+="正确率：{}/{}".format(self.correctNum,len(self.ans))
        s+="\n答题情况为（N表示没涂卡，T表示正确，F表示错误）："
        for i in range(1,len(self.checkState)):
            s+="\n"+str(i)+": "+self.checkState[i]
        self.textEdit.setText(s)