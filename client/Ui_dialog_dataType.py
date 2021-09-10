'''
Author: Radon
Date: 2021-04-22 14:26:43
LastEditTime: 2021-09-07 14:40:17
Description: 数据类型设置界面
'''
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\VSCode_Project\python_project\fuzzProject\dialog_seed_v2.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtWidgets
import sys
import json
import random
import re
import traceback
import os
import time
from loguru import logger

from PyQt5 import QtCore
# from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QHeaderView

import public
import staticAnalysis as sa

# 数据类型字典-start
# 存储数据类型的相关信息
dataTypeDict = {
    "bool": {
        "bitsize": 8,
        "lower": 0,
        "upper": 1
    },
    "char": {
        "bitsize": 8,
        "lower": -128, "upper": 127
    },
    "short": {
        "bitsize": 16,
        "lower": 0 - (1 << 15),
        "upper": (1 << 15) - 1
    },
    "short int": {
        "bitsize": 16,
        "lower": 0 - (1 << 15),
        "upper": (1 << 15) - 1
    },
    "int": {
        "bitsize": 32,
        "lower": 0 - (1 << 31),
        "upper": (1 << 31) - 1
    },
    "long": {
        "bitsize": 32,
        "lower": 0 - (1 << 31),
        "upper": (1 << 31) - 1
    },
    "long long": {
        "bitsize": 64,
        "lower": 0 - (1 << 63),
        "upper": (1 << 63) - 1
    },
    "unsigned char": {
        "bitsize": 8,
        "lower": 0,
        "upper": (1 << 8) - 1
    },
    "unsigned short": {
        "bitsize": 16,
        "lower": 0,
        "upper": (1 << 16) - 1
    },
    "unsigned short int": {
        "bitsize": 16,
        "lower": 0,
        "upper": (1 << 16) - 1
    },
    "unsigned int": {
        "bitsize": 32,
        "lower": 0,
        "upper": (1 << 32) - 1
    },
    "unsigned long": {
        "bitsize": 32,
        "lower": 0,
        "upper": (1 << 32) - 1
    },
    "unsigned long long": {
        "bitsize": 64,
        "lower": 0,
        "upper": (1 << 64) - 1
    },
    # TODO float和double的上下限太大了，看起来很长，所以暂时设置成了32位的上下限
    "float": {
        "bitsize": 32,
        "lower": float(0 - (1 << 31)),
        "upper": float((1 << 31) - 1)},
    "double": {
        "bitsize": 64,
        "lower": float(0 - (1 << 31)),
        "upper": float((1 << 31) - 1)
    }
}
# 数据类型字典-end


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        global dataTypeDict
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("自定义结构体成员变量值")
        Dialog.resize(1010, 510)
        self.setTable(Dialog)

        self.dialog = Dialog

    def setTable(self, Dialog):
        """界面函数

        Parameters
        ----------
        Dialog : QDialog
            [description]

        Notes
        -----
        [description]
        """
        global dataTypeDict

        # 表格-start
        self.dataTypeTable = QtWidgets.QTableWidget(Dialog)
        self.dataTypeTable.setGeometry(QtCore.QRect(10, 10, 880, 480))
        self.dataTypeTable.setColumnCount(4)
        # 表格-end

        # 添加按钮-start
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setGeometry(QtCore.QRect(900, 10, 100, 40))
        self.addBtn.setText("添加数据类型")
        self.addBtn.clicked.connect(self.addNewDataType)
        # self.addBtn.clicked.connect(self.saveData)
        # 添加按钮-end

        # 删除按钮-start
        self.delBtn = QtWidgets.QPushButton(Dialog)
        self.delBtn.setGeometry(QtCore.QRect(900, 60, 100, 40))
        self.delBtn.setText("删除数据类型")
        self.delBtn.clicked.connect(self.delDataType)
        # 删除按钮-end

        # 保存按钮-start
        self.saveBtn = QtWidgets.QPushButton(Dialog)
        self.saveBtn.setGeometry(QtCore.QRect(900, 110, 100, 40))
        self.saveBtn.setText("保存为JSON")
        self.saveBtn.clicked.connect(self.saveData)
        # 保存按钮-end

        self.setTableContent()

    def setTableContent(self):
        """设置表格内容

        Notes
        -----
        [description]
        """
        amountRows = len(dataTypeDict)  # 行数

        self.dataTypeTable.setRowCount(amountRows)
        self.dataTypeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.dataTypeTable.setHorizontalHeaderLabels(
            ["数据类型", "位", "下限", "上限"])

        i = 0  # 行
        for key, val in dataTypeDict.items():
            self.dataTypeTable.setItem(
                i, 0, self.enableeditItem(key))  # 数据类型名
            self.dataTypeTable.setCellWidget(
                i, 1, self.lineEditItem(True, str(val["bitsize"]), "bitsize", key))  # 位
            self.dataTypeTable.setCellWidget(
                i, 2, self.lineEditItem(True, str(val["lower"]), "lower", key))  # 下限
            self.dataTypeTable.setCellWidget(
                i, 3, self.lineEditItem(True, str(val["upper"]), "upper", key))  # 上限
            i += 1

    def enableeditItem(self, text):
        """生成表格中不可修改item

        Parameters
        ----------
        text : str
            表格中的文本

        Returns
        -------
        QTableWidgetItem
            [description]

        Notes
        -----
        [description]
        """
        enableeditItem = QtWidgets.QTableWidgetItem(text)
        enableeditItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return enableeditItem

    def lineEditItem(self, isNumber, placeholderText, whatThing, dataTypeName):
        """创建一个QLineEdit

        Parameters
        ----------
        isNumber : bool
            是否是数字
        placeholderText : str
            placeholder文本
        whatThing : str
            数据类型中的key值
        dataTypeName : str
            数据类型名称

        Returns
        -------
        QLineEdit
            [description]

        Notes
        -----
        [description]
        """
        global dataTypeDict
        lineEdit = QtWidgets.QLineEdit()
        if isNumber:
            # 输入框文本验证-start
            reg = QRegExp("^(\+)?\d+(\.\d+)?$")  # 正数、负数、小数-正则
            pValidator = QRegExpValidator()
            pValidator.setRegExp(reg)
            # 输入框文本验证-end
            lineEdit.setValidator(pValidator)  # 加入正则文本文本验证

        lineEdit.setPlaceholderText(placeholderText)

        lineEdit.editingFinished.connect(
            lambda: self.editFinish(lineEdit.text(), whatThing, dataTypeName))  # 编辑-活动
        return lineEdit

    def editFinish(self, text, whatThing, dataTypeName):
        global dataTypeDict
        try:
            dataTypeDict[dataTypeName][whatThing] = int(text)
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")

    def addNewDataType(self):
        """用户输入新数据类型的名称，并添加到字典中

        Notes
        -----
        [description]
        """
        global dataTypeDict
        try:
            newDataType, okPressed = QInputDialog.getText(
                self.dialog, "新增数据类型", "名称:", QtWidgets.QLineEdit.Normal, "")
            if okPressed:
                if len(newDataType) <= 0:
                    inputDataTypeBox = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Information, "消息", "请输入名称")
                    inputDataTypeBox.exec_()
                    return
                if newDataType in dataTypeDict.keys():
                    dataTypeExistBox = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Warning, "警告", "该数据类型已存在!")
                    dataTypeExistBox.exec_()
                    return
                dataTypeDict[newDataType] = {
                    "bitsize": 0, "lower": 0, "upper": 0}
                self.setTableContent()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            logger.exception("Exception in Ui_dialog_dataType, addNewDataType")
            addErrBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "错误", "出现错误:" + str(e))
            addErrBox.exec_()

    def delDataType(self):
        """用户输入要删除的删除类型，并从字典中删除

        Notes
        -----
        [description]
        """
        global dataTypeDict
        try:
            dataTypeName, okPressed = QInputDialog.getText(
                self.dialog, "删除数据类型", "请输入要删除的数据类型名称:", QtWidgets.QLineEdit.Normal, "")
            if okPressed and len(dataTypeName) > 0:
                dataTypeDict.pop(dataTypeName)
                self.setTableContent()
        except KeyError:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            logger.exception(
                "KeyError in Ui_dialog_dataType, delDataType func")
            delErrBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "删除失败:不存在此数据类型")
            delErrBox.exec_()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            logger.exception(
                "Exception in Ui_dialog_dataType, delDataType func")
            delErrBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "删除失败:" + str(e))
            delErrBox.exec_()

    def saveData(self):
        """将dataTypeDict保存为JSON文件
        Notes
        -----
        [description]
        """
        global dataTypeDict
        savePath = QtWidgets.QFileDialog.getSaveFileName(None, "save file", "C:/Users/Radon/Desktop",
                                                         "json file(*.json)")
        # 如果savePath[0]是空字符串的话，表示用户按了右上角的X
        if savePath[0] == "":
            return
        try:
            jsonFile = open(savePath[0], "w")
            json.dump(dataTypeDict, jsonFile)
            jsonFile.close()
            self.setTableContent()
            # 弹出保存成功的消息框
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, "消息", "保存成功!")
            saveMsgBox.exec_()
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")
            logger.exception("Exception in Ui_dialog_dataType, saveData func")
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "保存失败!\n" + repr(e))
            saveMsgBox.exec_()

    def initDataTypeDict(self, JSONPath):
        logger.info("init")
        if not os.path.exists(JSONPath):
            self.setDefaultDataTypeDict()
            return

        global dataTypeDict
        f = open(JSONPath)
        dataTypeDict = json.load(f)
        f.close()
        self.setTableContent()

    def setDefaultDataTypeDict(self):
        global dataTypeDict
        dataTypeDict = {    # dataTypeDict默认值
            "bool": {"bitsize": 8, "lower": 0, "upper": 1},
            "char": {"bitsize": 8, "lower": -128, "upper": 127},
            "short": {"bitsize": 16, "lower": 0 - (1 << 15), "upper": (1 << 15) - 1},
            "short int": {"bitsize": 16, "lower": 0 - (1 << 15), "upper": (1 << 15) - 1},
            "int": {"bitsize": 32, "lower": 0 - (1 << 31), "upper": (1 << 31) - 1},
            "long": {"bitsize": 32, "lower": 0 - (1 << 31), "upper": (1 << 31) - 1},
            "long long": {"bitsize": 64, "lower": 0 - (1 << 63), "upper": (1 << 63) - 1},
            "unsigned char": {"bitsize": 8, "lower": 0, "upper": (1 << 8) - 1},
            "unsigned short": {"bitsize": 16, "lower": 0, "upper": (1 << 16) - 1},
            "unsigned short int": {"bitsize": 16, "lower": 0, "upper": (1 << 16) - 1},
            "unsigned int": {"bitsize": 32, "lower": 0, "upper": (1 << 32) - 1},
            "unsigned long": {"bitsize": 32, "lower": 0, "upper": (1 << 32) - 1},
            "unsigned long long": {"bitsize": 64, "lower": 0, "upper": (1 << 64) - 1},
            "float": {"bitsize": 32, "lower": float(0 - (1 << 31)), "upper": float((1 << 31) - 1)},
            "double": {"bitsize": 64, "lower": float(0 - (1 << 31)), "upper": float((1 << 31) - 1)}
        }
        self.setTableContent()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     dialog = QtWidgets.QDialog()
#     ui = Ui_Dialog()
#     ui.setupUi(dialog)
#     dialog.show()
#     sys.exit(app.exec_())
