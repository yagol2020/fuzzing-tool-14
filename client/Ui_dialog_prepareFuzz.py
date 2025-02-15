'''
Author: Radon
Date: 2021-08-12 17:22:34
LastEditors: Radon
LastEditTime: 2021-10-09 14:14:40
Description: Hi, say something
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Project_VSCode\python\fuzzProject\client\dialog_prepareFuzz.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets

import Ui_dialog_fuzz as fuzzDialogPY
import utils
import re, os, traceback
import Ui_dialog_seed

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")

        Dialog.resize(464, 458)
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(40, 30, 381, 241))
        self.textBrowser.setObjectName("textBrowser")
        self.startTargetFuzzBtn = QtWidgets.QPushButton(Dialog)
        self.startTargetFuzzBtn.setEnabled(False)
        self.startTargetFuzzBtn.setGeometry(QtCore.QRect(40, 350, 181, 28))
        self.startTargetFuzzBtn.setObjectName("startTargetFuzzBtn")
        self.startNoTargetFuzzBtn = QtWidgets.QPushButton(Dialog)
        self.startNoTargetFuzzBtn.setEnabled(False)
        self.startNoTargetFuzzBtn.setGeometry(QtCore.QRect(240, 350, 181, 28))
        self.startNoTargetFuzzBtn.setObjectName("startNoTargetFuzzBtn")

        self.startAIFuzzBtn = QtWidgets.QPushButton(Dialog)
        self.startAIFuzzBtn.setEnabled(False)
        self.startAIFuzzBtn.setGeometry(QtCore.QRect(140, 390, 181, 28))
        self.startAIFuzzBtn.setObjectName("startAIFuzzBtn")

        self.senderLabel = QtWidgets.QLabel(Dialog)
        self.senderLabel.setGeometry(QtCore.QRect(120, 290, 61, 16))
        self.senderLabel.setObjectName("senderLabel")
        self.receiverLabel = QtWidgets.QLabel(Dialog)
        self.receiverLabel.setGeometry(QtCore.QRect(120, 320, 61, 16))
        self.receiverLabel.setObjectName("receiverLabel")
        self.senderIPLabel = QtWidgets.QLabel(Dialog)
        self.senderIPLabel.setGeometry(QtCore.QRect(180, 290, 181, 16))
        self.senderIPLabel.setObjectName("senderIPLabel")
        self.receiverIPLabel = QtWidgets.QLabel(Dialog)
        self.receiverIPLabel.setGeometry(QtCore.QRect(180, 320, 181, 16))
        self.receiverIPLabel.setObjectName("receiverIPLabel")

        # ==========connect================================================
        self.startTargetFuzzBtn.clicked.connect(self.startTargetFuzz)
        self.startTargetFuzzBtn.clicked.connect(Dialog.accept)
        self.startNoTargetFuzzBtn.clicked.connect(self.startNoTargetFuzz)
        self.startNoTargetFuzzBtn.clicked.connect(Dialog.accept)
        self.startAIFuzzBtn.clicked.connect(self.startAIFuzz)
        self.startAIFuzzBtn.clicked.connect(Dialog.accept)
        # =================================================================

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "确认"))
        self.textBrowser.setHtml(
            _translate(
                "Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">检验中...</p></body></html>"
            ))
        self.startTargetFuzzBtn.setText(_translate("Dialog", "开始目标制导模糊测试"))
        self.startNoTargetFuzzBtn.setText(_translate("Dialog", "开始无目标制导模糊测试"))
        self.startAIFuzzBtn.setText(_translate("Dialog", "开始交互接口规约模糊测试"))
        self.senderLabel.setText(_translate("Dialog", "发送方:"))
        self.receiverLabel.setText(_translate("Dialog", "接收方:"))
        self.senderIPLabel.setText(_translate("Dialog", "255.255.255.255:65535"))
        self.receiverIPLabel.setText(_translate("Dialog", "255.255.255.255:65535"))

    # ==========定义功能================================================================
    def setValues(self, ui, header_loc_list, IPAddressList):
        """设置初始值

        Parameters
        ----------
        ui : Ui_dialog
            客户端的ui
        header_loc_list : list
            存储了每个header的绝对地址，每个地址是str
        IPAddressList : list
            发送方与接收方的IP地址(str)列表，[0]是发送方，[1]是接收方

        Notes
        -----
        [description]
        """
        self.ui = ui
        self.header_loc_list = header_loc_list

        root_loc = os.path.join(os.path.dirname(header_loc_list[0]), "in")
        self.textBrowser.clear()

        # 查看是否已设置IP地址
        IPAddressValidation = True
        if len(IPAddressList[0]) == 0:
            self.senderIPLabel.setText("未设置")
            IPAddressValidation = False
        else:
            self.senderIPLabel.setText(IPAddressList[0])
        if len(IPAddressList[1]) == 0:
            self.receiverIPLabel.setText("未设置")
            IPAddressValidation = False
        else:
            self.receiverIPLabel.setText(IPAddressList[1])

        # 查看当前目录下是否有in文件夹
        if not os.path.exists(root_loc):
            self.textBrowser.append("<font color='red'>X 头文件根目录下不存在in文件夹</font>")
            return
        self.textBrowser.append("<font color='green'>√ 头文件根目录下存在in文件夹</font>")

        # 查看in文件夹中是否有mutate.c, input.json, checkCodeMethod.txt, header_loc_list.txt, seed, callgraph.txt, insFunc.dll, nodes.txt
        filesForNoTarget = [
            "mutate.c", "mutate.dll", "input.json", "checkCodeMethod.txt", "header_loc_list.txt", "seed", "callgraph.txt", "insFunc.dll", "nodes.txt"
        ]
        noTargetFilesValidation = True
        for file in filesForNoTarget:
            if os.path.exists(os.path.join(root_loc, file)):
                self.textBrowser.append("<font color='green'>√ %s</font>" % ("已检测到" + file))
                if file == "mutate.c":
                    cJSONRootPath = os.path.dirname(os.path.abspath(__file__))      # 使用copy命令将cJSON.c与cJSON.h复制到in目录下
                    copyCmd = "copy " + os.path.join(cJSONRootPath, "*cJSON*") + " " + root_loc
                    os.system(copyCmd)
                    os.system("gcc -shared -o " + os.path.join(root_loc, "mutate.dll") + " " + os.path.join(root_loc, "mutate.c") + " " + os.path.join(root_loc, "cJSON.c"))
            else:
                self.textBrowser.append("<font color='red'>X %s</font>" % ("未检测到" + file))
                noTargetFilesValidation = False

        # 查看in文件夹中是否有saresult.txt
        filesForTarget = ["saresult.txt"]
        targetFilesValidation = True
        for file in filesForTarget:
            if os.path.exists(os.path.join(root_loc, file)):
                self.textBrowser.append("<font color='green'>√ %s</font>" % ("已检测到" + file))
            else:
                self.textBrowser.append("<font color='red'>X %s</font>" % ("未检测到" + file))
                targetFilesValidation = False
        # 如果没有填IP，就没法开始测试
        if IPAddressValidation:
            # 如果客户端与服务端的完整性验证均通过，则可以开始目标制导的模糊测试
            # 如果客户端通过，服务端不通过，则可以开始无目标制导的模糊测试
            # 如果客户端不通过，服务端通过或两者均不通过，则无法开始模糊测试
            if noTargetFilesValidation and targetFilesValidation:
                self.textBrowser.append("<font color='green'>- %s</font>" % ("可以开始目标制导的模糊测试"))
                self.startTargetFuzzBtn.setEnabled(True)
                self.startNoTargetFuzzBtn.setEnabled(True)

                self.startAIFuzzBtn.setEnabled(True)
                # 设置目标
                self.targetSet = open(os.path.join(root_loc, "saresult.txt")).read().split("\n")
                self.targetSet.pop(-1)
                # 所有函数结点
                self.allNodes = open(os.path.join(root_loc, "nodes.txt")).read().split("\n")
                self.allNodes.pop(-1)
            elif noTargetFilesValidation and not targetFilesValidation:
                self.textBrowser.append("<font color='orange'>- %s</font>" % ("可以开始无目标制导的模糊测试"))
                self.startNoTargetFuzzBtn.setEnabled(True)
                # self.startAIFuzzBtn.setEnabled(True)

            else:
                self.textBrowser.append("<font color='red'>- %s</font>" % ("无法开始模糊测试，请尝试重新生成文件"))
        else:
            self.textBrowser.append("<font color='red'>- %s</font>" % ("请填写IP地址"))

    def startTargetFuzz(self):
        root_loc = os.path.dirname(self.header_loc_list[0])
        # 检查是否存在out文件夹
        if os.path.exists(os.path.join(root_loc, "out")):
            outFolderExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, "消息", "当前目录下存在out文件夹，是否覆盖?")
            yes = outFolderExistBox.addButton("是", QtWidgets.QMessageBox.YesRole)
            no = outFolderExistBox.addButton("否", QtWidgets.QMessageBox.NoRole)
            outFolderExistBox.exec_()
            if outFolderExistBox.clickedButton() == no:
                backupOutFolderBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "您可以先备份当前out文件夹")
                backupOutFolderBox.exec_()
                return

        # 提示用户插装变量初始值需要为0
        confirmInsVarInitValueBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请确认插装变量初值为0")
        yes = confirmInsVarInitValueBox.addButton("确认", QtWidgets.QMessageBox.YesRole)
        no = confirmInsVarInitValueBox.addButton("取消", QtWidgets.QMessageBox.NoRole)
        confirmInsVarInitValueBox.exec_()
        if confirmInsVarInitValueBox.clickedButton() == no:
            modifyInsVarInitValueBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请修改插装变量的初始值")
            modifyInsVarInitValueBox.exec_()
            return

        try:
            self.fuzzDialog = QtWidgets.QDialog()
            self.fuzzDialog.setWindowTitle("目标制导模糊测试")
            self.uiFuzz = fuzzDialogPY.Ui_Dialog()
            self.uiFuzz.setupUi(self.fuzzDialog, False)
            self.fuzzDialog.show()
            self.uiFuzz.startFuzz(self.header_loc_list, self.ui, self, self.uiFuzz)
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            fuzzErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "发生错误:" + str(e))
            fuzzErrBox.show()

    def startNoTargetFuzz(self):
        root_loc = os.path.dirname(self.header_loc_list[0])
        # 检查是否存在out文件夹
        if os.path.exists(os.path.join(root_loc, "out")):
            outFolderExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, "消息", "当前目录下存在out文件夹，是否覆盖?")
            yes = outFolderExistBox.addButton("是", QtWidgets.QMessageBox.YesRole)
            no = outFolderExistBox.addButton("否", QtWidgets.QMessageBox.NoRole)
            outFolderExistBox.exec_()
            if outFolderExistBox.clickedButton() == no:
                backupOutFolderBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "您可以先备份当前out文件夹")
                backupOutFolderBox.exec_()
                return

        # 提示用户插装变量初始值需要为0
        confirmInsVarInitValueBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请确认插装变量初值为0")
        yes = confirmInsVarInitValueBox.addButton("确认", QtWidgets.QMessageBox.YesRole)
        no = confirmInsVarInitValueBox.addButton("取消", QtWidgets.QMessageBox.NoRole)
        confirmInsVarInitValueBox.exec_()
        if confirmInsVarInitValueBox.clickedButton() == no:
            modifyInsVarInitValueBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请修改插装变量的初始值")
            modifyInsVarInitValueBox.exec_()
            return

        try:
            self.targetSet = list()
            self.fuzzDialog = QtWidgets.QDialog()
            self.fuzzDialog.setWindowTitle("无目标模糊测试")
            self.uiFuzz = fuzzDialogPY.Ui_Dialog()
            self.uiFuzz.setupUi(self.fuzzDialog, False)
            self.uiFuzz.startFuzz(self.header_loc_list, self.ui, self, self.uiFuzz)
            self.fuzzDialog.show()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            fuzzErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "发生错误:" + str(e))
            fuzzErrBox.show()

    # ==========定义功能================================================================

    def startAIFuzz(self):
        root_loc = os.path.dirname(self.header_loc_list[0])

        if self.ui.ProtocolFuzzCfgDialog is None:
            fuzzErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "请正确配置测试参数！")
            fuzzErrBox.exec_()
            return

        # if self.ui.ProtocolFuzzCfgDialog.existTS.isChecked() and self.ui.ProtocolFuzzCfgDialog.tsLoc.toPlainText() == "":
        #     msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "请确保已将初始训练集拷贝到" + os.path.join(root_loc, "AIFuzz", "seeds") + "目录下！")
        #     msg.addButton("确定", QtWidgets.QMessageBox.YesRole)
        #     msg.exec_()

        try:
            self.fuzzDialog = QtWidgets.QDialog()
            self.fuzzDialog.setWindowTitle("基于机器学习的模糊测试")
            self.uiFuzz = fuzzDialogPY.Ui_Dialog()
            self.uiFuzz.setupUi(self.fuzzDialog, True)
            self.uiFuzz.startFuzz(self.header_loc_list, self.ui, self, self.uiFuzz)
            self.fuzzDialog.show()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            fuzzErrBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "发生错误:" + str(e))
            fuzzErrBox.show()
