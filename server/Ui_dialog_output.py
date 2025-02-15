'''
Author: 金昊宸
Date: 2021-04-22 14:26:43
LastEditTime: 2021-10-30 15:16:11
Description: 网络通信的输出设置界面
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

from PyQt5 import QtCore
# from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMessageBox, QHeaderView

import public
import staticAnalysis as sa

# 传入数据结构-start
from util.get_comment_from_struct import handle_struct

structDict = {
    "结构体名1": {
        "变量名11": {
            "value": None,
            "lower": 10,
            "upper": 200,
            "instrument": False,
            "bitsize": 8,
            "comment": "占位"
        },
        "变量名12": {
            "value": None,
            "lower": 300,
            "upper": 500,
            "instrument": False,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位"
        }
    },
    "结构体名2": {
        "变量名21": {
            "value": "var3",
            "lower": 30,
            "upper": 50,
            "instrument": False,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位"
        },
        "变量名22": {
            "value": "var4",
            "lower": 10,
            "upper": 30,
            "instrument": False,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位"
        },
        "变量名23": {
            "value": "var5",
            "lower": 300,
            "upper": 500,
            "instrument": False,
            "mutation": True,
            "bitsize": 8,
            "comment": "占位"
        },
    }
}
# 传入数据结构-end

# 数据类型字典-start
# 存储数据类型得上下限与位
dataTypeDict = {
    "bool": {
        "bitsize": 8,
        "lower": 0,
        "upper": 1
    },
    "char": {
        "bitsize": 8,
        "lower": -128,
        "upper": 127
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
        "upper": float((1 << 31) - 1)
    },
    "double": {
        "bitsize": 64,
        "lower": float(0 - (1 << 31)),
        "upper": float((1 << 31) - 1)
    }
}
# 数据类型字典-end


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        global structDict
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("自定义结构体成员变量值")
        Dialog.resize(900, 550)
        self.setTable(Dialog)

    def setTable(self, Dialog):  # 界面函数
        global structDict

        # 表格-start
        self.structTable = QtWidgets.QTableWidget(Dialog)
        self.structTable.setGeometry(QtCore.QRect(10, 10, 880, 480))
        self.structTable.setColumnCount(5)
        # 表格-end

        # 保存按钮-start
        self.determineBtn = QtWidgets.QPushButton(Dialog)
        self.determineBtn.setGeometry(QtCore.QRect(10, 500, 435, 40))
        self.determineBtn.setText("保存为JSON")
        self.determineBtn.clicked.connect(self.saveData)
        # 保存按钮-end

        # 生成按钮-start
        self.generateBtn = QtWidgets.QPushButton(Dialog)
        self.generateBtn.setGeometry(QtCore.QRect(455, 500, 435, 40))
        self.generateBtn.setText("生成插装文件")
        self.generateBtn.clicked.connect(self.genNecessaryFile)
        # self.generateBtn.clicked.connect(Dialog.accept)
        # 生成按钮-end

        structDict = {"struct": {"var": {"bitsize": 8, "comment": "注释", "instrument": False}}}
        self.setTableContent(structDict)

    # 发送一个新的dict，设置表格内容

    def setTableContent(self, newDict):
        # 获取变量数-start
        amountRows = 0
        for key, val in structDict.items():
            amountRows += len(val)
        # 获取变量数-end
        self.structTable.setRowCount(amountRows)
        self.structTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.structTable.setHorizontalHeaderLabels(['结构体', '成员变量', "位", "注释", "是否插装变量"])

        i = 0  # 行
        j = 0  # 列
        self.insCheckBoxItemDict = structDict  # 插装变量复选框的字典
        # 不可编辑的item
        for key, val in structDict.items():
            structKey = key  # 结构体名
            for key, val in val.items():
                self.structTable.setItem(i, 0, self.enableeditItem(structKey))  # 结构体名
                self.structTable.setItem(i, 1, self.enableeditItem(key))  # 成员变量名
                self.structTable.setItem(i, 2, self.enableeditItem(str(val["bitsize"])))  # 位
                self.structTable.setItem(i, 3, self.enableeditItem(str(val["comment"])))  # 注释
                self.structTable.setCellWidget(i, 4, self.insCheckBoxItem(val['instrument'], structKey, key))  # 插装
                i += 1

    # 结束

    def enableeditItem(self, text):  # 生成不可修改item
        enableeditItem = QtWidgets.QTableWidgetItem(text)
        enableeditItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return enableeditItem

    # 表格插装-start
    def insCheckBoxItem(self, checkBool, struct, memVal):
        global structDict
        checkBox = QtWidgets.QCheckBox()
        checkBox.setChecked(checkBool)
        checkBox.stateChanged.connect(lambda: self.insCheckChange(checkBox.isChecked(), struct, memVal))
        self.insCheckBoxItemDict[struct][memVal]['checkBox'] = checkBox
        return checkBox

    def insCheckChange(self, checkBool, struct, memVal):  # CheckBox修改函数
        global structDict
        for key, val in self.insCheckBoxItemDict.items():
            for key, val in val.items():
                if val['instrument']:
                    val['checkBox'].setChecked(False)
        structDict[struct][memVal]['instrument'] = checkBool
        # print(structDict)

    # 表格插装-end

    def saveData(self):
        """将structDict保存为JSON文件

        Notes
        -----
        [description]
        """
        global structDict
        savePath = QtWidgets.QFileDialog.getSaveFileName(None, "save file", r"C:\Users\Radon\Desktop", "json file(*.json)")
        # 如果savePath[0]是空字符串的话，表示用户按了右上角的X
        if savePath[0] == "":
            return
        try:
            jsonFile = open(savePath[0], "w")
            self.delCheckBox()
            json.dump(structDict, jsonFile)
            jsonFile.close()
            self.setTableContent(structDict)
            # 弹出保存成功的消息框
            saveMsgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "保存成功!")
            saveMsgBox.exec_()
        except BaseException as e:
            traceback.print_exc()
            saveMsgBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "保存失败!\n" + repr(e))
            saveMsgBox.exec_()

    def delCheckBox(self):  # 清空字典中delcheckbox
        global structDict
        for key, val in structDict.items():
            for key, val in val.items():
                if 'checkBox' in val.keys():
                    del val['checkBox']

    def getBitsize(self, variable):
        """根据变量的名称获取它的位大小

        Parameters
        ----------
        variable : str
            变量的名称

        Returns
        -------
        int
            返回值是一个int类型的数值，表示了它占多少位

        Notes
        -----
        [description]
        """
        if ":" in variable:
            return int(re.sub(" ", "", variable.split(":")[1]))
        else:
            # 在数据类型字典里找对应的位大小
            variable = variable.split(" ")
            variable.pop(-1)
            dataType = " ".join(variable).rstrip()
            for key, value in dataTypeDict.items():
                if key == dataType:
                    return value["bitsize"]
            return -1

    def initStructDict(self, header_loc_list, JSONPath, readJSON, ui, struct, allStruct):
        """根据传入的路径分析头文件，或直接读取现有的json文件

        Parameters
        ----------
        header_loc_list : list
            列表，其中存储了所有头文件的位置
        JSONPath : str
            JSON文件的存储路径
        readJSON : Bool
            是否读取已有的json
        ui : Ui_Dialog
            主界面
        struct : str
            选择的结构体名称
        allStruct : list
            存储了所有结构体的名称

        Returns
        -------
        [type]
            [description]

        Notes
        -----
        [description]
        """
        self.header_loc_list = header_loc_list
        self.struct = struct
        self.uiSelectIOStruct = ui
        global structDict
        structDict.clear()
        if readJSON:
            f = open(JSONPath, "r")
            structDict = json.load(f)
            self.struct = list(structDict.keys())[0]
            f.close()
        else:
            # structInfo是一个List(tuple(name, loc)), 存储了可设置初始值的成员变量名称和它所在的位置
            structInfo = sa.getOneStruct(header_loc_list, struct, "", allStruct)
            typedefDict = sa.getTypedefDict(header_loc_list)

            tempDict = {}
            # 分析并设置structDict的值
            for i in range(0, len(structInfo)):
                tempDict[structInfo[i][0]] = {"value": None, "lower": 0, "upper": 999, "instrument": False, "mutation": False, "bitsize": -1}
                tempDict[structInfo[i][0]]["loc"] = structInfo[i][1]
                # 如果用户指定了位大小
                if ":" in structInfo[i][0]:
                    tempDict[structInfo[i][0]]["bitsize"] = self.getBitsize(structInfo[i][0])
                    if "unsigned" in structInfo[i][0]:
                        tempDict[structInfo[i][0]]["upper"] = 2**tempDict[structInfo[i][0]]["bitsize"] - 1
                        tempDict[structInfo[i][0]]["lower"] = 0
                    else:
                        tempDict[structInfo[i][0]]["upper"] = 2**(tempDict[structInfo[i][0]]["bitsize"] - 1) - 1
                        tempDict[structInfo[i][0]]["lower"] = 0 - \
                            (2 ** tempDict[structInfo[i][0]]["bitsize"] - 1)
                else:
                    # 如果用户没指定位大小，自动获取
                    # dataType: 表示数据类型，从list变为str
                    tempDict[structInfo[i][0]]["bitsize"] = self.getBitsize(structInfo[i][0])
                    dataType = structInfo[i][0].split(" ")
                    dataType.pop(-1)
                    dataType = " ".join(dataType)
                    try:
                        if not dataType in dataTypeDict.keys():
                            dataType = typedefDict[dataType]

                        if tempDict[structInfo[i][0]]["bitsize"] == -1:
                            tempDict[structInfo[i][0]]["bitsize"] = dataTypeDict[dataType]["bitsize"]
                        tempDict[structInfo[i][0]]["upper"] = dataTypeDict[dataType]["upper"]
                        tempDict[structInfo[i][0]]["lower"] = dataTypeDict[dataType]["lower"]
                    except BaseException as e:
                        print("分析" + dataType + "类型时出错:", e)
                        tempDict[structInfo[i][0]]["upper"] = 999
                        tempDict[structInfo[i][0]]["lower"] = -999
            structDict[struct] = tempDict
        structDict = handle_struct(struct_dict=structDict)
        # 设置Table
        self.setTableContent(structDict)

    def genNecessaryFile(self):
        """生成输出结构体所需的一些必要文件

        Notes
        -----
        生成的必要文件分别有：
        instrument.txt: 记录了插装的变量
        outputStruct.txt: 记录了输出结构体的名称
        """
        # 1.生成instrument.txt
        root_loc = os.path.join(os.path.dirname(self.header_loc_list[0]), "in")
        if not os.path.exists(root_loc):
            os.mkdir(root_loc)
        f = open(os.path.join(root_loc, "instrument.txt"), mode="w")
        instrumentFlag = False
        for key, value in structDict[self.struct].items():
            if value["instrument"]:
                with open(os.path.join(root_loc, "instrument.txt"), mode="w") as f:
                    f.write(key)
                instrumentFlag = True
                break

        # 创建outputStruct.txt
        f = open(os.path.join(root_loc, "outputStruct.txt"), mode="w")
        f.write(self.struct)
        f.close()

        # 如果没选择插装变量则跳出警告
        if not instrumentFlag:
            noInstrumentValueBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "没有选择插装变量!")
            noInstrumentValueBox.exec_()
            return

        genSuccessBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "生成成功!\n")
        genSuccessBox.exec_()

    # 结束


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    headerNotExistBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
    headerNotExistBox.exec_()

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     dialog = QtWidgets.QDialog()
#     ui = Ui_Dialog()
#     ui.setupUi(dialog)
#     dialog.show()
#     sys.exit(app.exec_())
