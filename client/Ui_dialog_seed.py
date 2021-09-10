'''
Author: 金昊宸
Date: 2021-04-22 14:26:43
LastEditTime: 2021-09-10 15:26:42
Description: 网络通信的输入设置界面
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
import ctypes, _ctypes

from PyQt5 import QtCore
# from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMessageBox, QHeaderView

import public
import staticAnalysis as sa

# 传入数据结构-start
from util.check_code import get_support_methods, calculate_check_code_from_dec
from util.get_comment_from_struct import handle_struct

structDict = {
    "结构体名1": {
        "变量名11": {
            "value": None,
            "lower": 10,
            "upper": 200,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        },
        "变量名12": {
            "value": None,
            "lower": 300,
            "upper": 500,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        }
    },
    "结构体名2": {
        "变量名21": {
            "value": "var3",
            "lower": 30,
            "upper": 50,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        },
        "变量名22": {
            "value": "var4",
            "lower": 10,
            "upper": 30,
            "mutation": False,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        },
        "变量名23": {
            "value": "var5",
            "lower": 300,
            "upper": 500,
            "mutation": True,
            "bitsize": 8,
            "comment": "占位",
            "checkCode": False,
            "checkField": False
        },
    }
}
# 传入数据结构-end

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
        global structDict
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("自定义结构体成员变量值")
        Dialog.resize(1110, 510)
        self.setTable(Dialog)

    def setTable(self, Dialog):  # 界面函数
        global structDict

        # 表格-start
        self.structTable = QtWidgets.QTableWidget(Dialog)
        self.structTable.setGeometry(QtCore.QRect(10, 10, 880, 480))
        self.structTable.setColumnCount(11)
        # 表格-end

        # 保存按钮-start
        self.determineBtn = QtWidgets.QPushButton(Dialog)
        self.determineBtn.setGeometry(QtCore.QRect(900, 76, 200, 35))
        self.determineBtn.setText("保存为JSON")
        self.determineBtn.clicked.connect(self.saveData)
        # 保存按钮-end

        # 全变异按钮-start
        self.allMutateBtn = QtWidgets.QPushButton(Dialog)
        self.allMutateBtn.setGeometry(QtCore.QRect(900, 121, 200, 35))
        self.allMutateBtn.setText("全部变异")
        self.allMutateBtn.clicked.connect(self.setAllVariableMutate)
        # 全变异按钮-end

        # 全不变异按钮-start
        self.allNotMutateBtn = QtWidgets.QPushButton(Dialog)
        self.allNotMutateBtn.setGeometry(QtCore.QRect(900, 166, 200, 35))
        self.allNotMutateBtn.setText("全部不变异")
        self.allNotMutateBtn.clicked.connect(self.setAllVariableNotMutate)
        # 全不变异按钮-end

        # 全校验码按钮-start
        self.allCheckCodeBtn = QtWidgets.QPushButton(Dialog)
        self.allCheckCodeBtn.setGeometry(QtCore.QRect(900, 211, 200, 35))
        self.allCheckCodeBtn.setText("全部设置为校验字段")
        self.allCheckCodeBtn.clicked.connect(self.setAllVariableCheckField)
        # 全校验码按钮-end

        # 全不校验码按钮-start
        self.allNotCheckCodeBtn = QtWidgets.QPushButton(Dialog)
        self.allNotCheckCodeBtn.setGeometry(QtCore.QRect(900, 256, 200, 35))
        self.allNotCheckCodeBtn.setText("全部不设置为校验字段")
        self.allNotCheckCodeBtn.clicked.connect(self.setAllVariableNotCheckField)
        # 全不校验码按钮-end

        # 生成按钮-start
        self.generateBtn = QtWidgets.QPushButton(Dialog)
        self.generateBtn.setGeometry(QtCore.QRect(900, 301, 200, 35))
        self.generateBtn.setText("生成种子文件")
        self.generateBtn.clicked.connect(self.genSeed)
        # 生成按钮-end

        # 校验算法label-start
        self.checkCodeMethodLabel = QtWidgets.QLabel(Dialog)
        self.checkCodeMethodLabel.setGeometry(QtCore.QRect(900, 5, 200, 31))
        self.checkCodeMethodLabel.setObjectName("checkCodeMethodLabel")
        self.checkCodeMethodLabel.setText("校验算法:")
        # 校验算法label-end

        # 下拉菜单选择校验算法-start
        self.checkCodeComboBox = QtWidgets.QComboBox(Dialog)
        self.checkCodeComboBox.setGeometry(QtCore.QRect(900, 35, 200, 31))
        self.checkCodeComboBox.setObjectName("checkCodeComboBox")
        # 添加项目
        check_code_methods = get_support_methods()
        for index in range(len(check_code_methods)):
            self.checkCodeComboBox.addItem("")
            self.checkCodeComboBox.setItemText(index, check_code_methods[index])
        # 下拉菜单选择校验算法-end

        structDict = {
            "struct": {
                "var": {
                    "value": 2,
                    "lower": 0,
                    "upper": 255,
                    "bitsize": 8,
                    "comment": "注释",
                    "mutation": False,
                    "checkCode": False,
                    "checkField": False
                }
            }
        }
        self.setTableContent()

    # 发送一个新的dict，设置表格内容
    def setTableContent(self):
        # 获取变量数-start
        amountRows = 0
        for key, val in structDict.items():
            amountRows += len(val)
        # 获取变量数-end
        self.structTable.setRowCount(amountRows)
        self.structTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.structTable.setHorizontalHeaderLabels(
            ["结构体", "成员变量", "当前值", "范围下限", "范围上限", "位", "注释", "是否变异", "校验码", "校验字段", "是否大小端转换"])

        i = 0  # 行
        j = 0  # 列
        self.checkCodeCheckBoxItemDict = structDict  # 校验码复选框字典
        # 不可编辑的item
        for key, val in structDict.items():
            structKey = key  # 结构体名
            for key, val in val.items():
                self.structTable.setItem(
                    i, 0, self.enableeditItem(structKey))  # 结构体名
                self.structTable.setItem(
                    i, 1, self.enableeditItem(key))  # 成员变量名
                # if val["value"]==None:
                #     structDict[structKey][key]["value"] = self.getRanNum(
                #         val["lower"], val["upper"])
                self.structTable.setCellWidget(
                    i, 2, self.lineEditItem(True, val["value"], "value", structKey, key))  # 当前值
                self.structTable.setCellWidget(
                    i, 3, self.lineEditItem(True, val["lower"], "lower", structKey, key))  # 下限
                self.structTable.setCellWidget(
                    i, 4, self.lineEditItem(True, val["upper"], "upper", structKey, key))  # 上限
                self.structTable.setItem(
                    i, 5, self.enableeditItem(str(val["bitsize"])))  # 位
                self.structTable.setItem(
                    i, 6, self.enableeditItem(str(val["comment"])))  # 注释
                self.structTable.setCellWidget(
                    i, 7, self.varCheckBoxItem(val["mutation"], structKey, key))  # 变异
                self.structTable.setCellWidget(
                    i, 8, self.checkCodeCheckBoxItem(val["checkCode"], structKey, key))  # 校验码
                self.structTable.setCellWidget(
                    i, 9, self.checkFieldCheckBoxItem(val["checkField"], structKey, key))  # 校验字段
                i += 1

    # 结束

    def enableeditItem(self, text):  # 生成不可修改item
        enableeditItem = QtWidgets.QTableWidgetItem(text)
        enableeditItem.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return enableeditItem

    # 表格变异-CheckBox-start
    def varCheckBoxItem(self, checkBool, struct, memVal):
        global structDict
        checkBox = QtWidgets.QCheckBox()
        checkBox.setChecked(checkBool)
        checkBox.stateChanged.connect(
            lambda: self.varCheckChange(checkBox.isChecked(), struct, memVal))
        return checkBox

    def varCheckChange(self, checkBool, struct, memVal):  # CheckBox修改函数
        global structDict
        structDict[struct][memVal]["mutation"] = checkBool
    # 表格变异-CheckBox-end

    # 表格校验码变量-CheckBox-start
    def checkCodeCheckBoxItem(self, checkBool, struct, memVal):
        global structDict
        checkBox = QtWidgets.QCheckBox()
        checkBox.setChecked(checkBool)
        checkBox.stateChanged.connect(
            lambda: self.checkCodeCheckChange(checkBox.isChecked(), struct, memVal))
        self.checkCodeCheckBoxItemDict[struct][memVal]["checkCodeCheckBox"] = checkBox
        return checkBox

    def checkCodeCheckChange(self, checkBool, struct, memVal):  # CheckBox修改函数
        global structDict
        for key, val in self.checkCodeCheckBoxItemDict.items():
            for key, val in val.items():
                if val["checkCode"]:
                    val["checkCodeCheckBox"].setChecked(False)
        structDict[struct][memVal]["checkCode"] = checkBool
        # 校验码与校验字段不能重复
        if structDict[struct][memVal]["checkField"] and checkBool:
            structDict[struct][memVal]["checkFieldCheckBox"].setChecked(False)
            structDict[struct][memVal]["checkField"] = False

    # 表格插装变量-CheckBox-end

    # 表格校验字段-CheckBox-start
    def checkFieldCheckBoxItem(self, checkBool, struct, memVal):
        global structDict
        checkBox = QtWidgets.QCheckBox()
        checkBox.setChecked(checkBool)
        structDict[struct][memVal]["checkFieldCheckBox"] = checkBox
        checkBox.stateChanged.connect(
            lambda: self.checkFieldCheckChange(checkBox.isChecked(), struct, memVal))
        return checkBox

    def checkFieldCheckChange(self, checkBool, struct, memVal):  # CheckBox修改函数
        global structDict
        structDict[struct][memVal]["checkField"] = checkBool
        # 校验字段与校验码不能是同一个变量
        if structDict[struct][memVal]["checkCode"] and checkBool:
            structDict[struct][memVal]["checkCodeCheckBox"].setChecked(False)
            structDict[struct][memVal]["checkCode"] = False

    # 表格校验字段-CheckBox-end

    # 表格-LineEdit-start
    def lineEditItem(self, isNumber, placeholderText, whatThing, struct, memVal):
        global structDict
        lineEdit = QtWidgets.QLineEdit()
        # print(isNumber, placeholderText, whatThing, struct, memVal)
        if isNumber:
            # 输入框文本验证-start
            reg = QRegExp("^(\-|\+)?\d+(\.\d+)?$")  # 正数、负数、小数-正则
            pValidator = QRegExpValidator()
            pValidator.setRegExp(reg)
            # 输入框文本验证-end
            lineEdit.setValidator(pValidator)  # 加入正则文本文本验证

        if whatThing == "value" and placeholderText == None:
            # 获取数据类型，并根据类型设置是浮点类型的值还是整数
            dataType = memVal.split(" ")
            dataType.pop(-1)
            dataType = " ".join(dataType)
            if "float" in dataType or "double" in dataType:
                structDict[struct][memVal]["value"] = self.getRanFloatNum(
                    structDict[struct][memVal]["lower"], structDict[struct][memVal]["upper"])
                lineEdit.setPlaceholderText(
                    "随机值(%.2f)" % structDict[struct][memVal]["value"])  # 浮点型默认文字
            else:
                structDict[struct][memVal]["value"] = self.getRanIntNum(
                    structDict[struct][memVal]["lower"], structDict[struct][memVal]["upper"])
                lineEdit.setPlaceholderText(
                    "随机值(%d)" % structDict[struct][memVal]["value"])  # 整型默认文字
        else:
            lineEdit.setPlaceholderText(str(placeholderText))

        # print(lineEdit.hasFocus())
        lineEdit.editingFinished.connect(
            lambda: self.editFinish(lineEdit.text(), whatThing, struct, memVal, lineEdit))  # 编辑-活动
        return lineEdit

    def editFinish(self, text, whatThing, struct, memVal, lineEdit):
        global structDict
        # lineEdit.hasFocus()
        # 获取变量上下限可以改的范围，防止用户修改上下限后导致溢出
        try:
            if ":" in memVal:
                if "unsigned" in memVal:
                    maxUpper = 2 ** structDict[struct][memVal]["bitsize"] - 1
                    minLower = 0
                else:
                    maxUpper = 2 ** (structDict[struct][memVal]["bitsize"] - 1) - 1
                    minLower = 0 - 2 ** (structDict[struct][memVal]["bitsize"] - 1)
            else:
                dataType = memVal.split(" ")
                dataType.pop(-1)
                dataType = " ".join(dataType)
                maxUpper = dataTypeDict[dataType]["upper"]
                minLower = dataTypeDict[dataType]["lower"]
        except BaseException as e:
            print("获取上下限时出错:", e, "将默认为int的上下限\033[1;31m")
            traceback.print_exc()
            print("\033[0m")

        dataType = memVal.split(" ")
        dataType.pop(-1)
        dataType = " ".join(dataType)
        # 如果编辑的是值的内容
        if text != "" and whatThing == "value":
            # 数值范围验证
            if float(text) <= structDict[struct][memVal]["upper"] and float(text) >= structDict[struct][memVal][
                "lower"]:
                if "float" in dataType or "double" in dataType:
                    structDict[struct][memVal][whatThing] = float(text)
                else:
                    structDict[struct][memVal][whatThing] = int(float(text))
            else:
                # 超范围错误提醒-start
                msg_box = QMessageBox(
                    QMessageBox.Warning, "错误",
                    "请输入%s-%s内的值" % (structDict[struct][memVal]["lower"], structDict[struct][memVal]["upper"]))
                msg_box.exec_()
                lineEdit.clear()
                # 超范围错误提醒-end

        outOfRangeBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "设置的值超出范围，有溢出风险!")
        # 如果编辑的是下限的内容
        if whatThing == "lower":
            if float(text) < minLower or float(text) > maxUpper:
                outOfRangeBox.exec_()
                lineEdit.clear()
            else:
                if "float" in dataType or "double" in dataType:
                    structDict[struct][memVal][whatThing] = float(text)
                else:
                    structDict[struct][memVal][whatThing] = int(text)

        # 如果编辑的是上限的内容
        if whatThing == "upper":
            if float(text) < minLower or float(text) > maxUpper:
                lineEdit.clear()
                outOfRangeBox.exec_()
            else:
                if "float" in dataType or "double" in dataType:
                    structDict[struct][memVal][whatThing] = float(text)
                else:
                    structDict[struct][memVal][whatThing] = int(text)

    def saveData(self):
        """将structDict保存为JSON文件
        Notes
        -----
        [description]
        """
        global structDict
        savePath = QtWidgets.QFileDialog.getSaveFileName(None, "save file", "C:/Users/Radon/Desktop",
                                                         "json file(*.json)")
        # 如果savePath[0]是空字符串的话，表示用户按了右上角的X
        if savePath[0] == "":
            return
        try:
            jsonFile = open(savePath[0], "w")
            self.delCheckBox()
            json.dump(structDict, jsonFile)
            jsonFile.close()
            self.setTableContent()
            # 弹出保存成功的消息框
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, "消息", "保存成功!")
            saveMsgBox.exec_()
        except BaseException as e:
            traceback.print_exc()
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "保存失败!\n" + repr(e))
            saveMsgBox.exec_()

    def delCheckBox(self):  # 清空字典中checkbox
        global structDict
        for key, val in structDict.items():
            for key, val in val.items():
                if "checkCodeCheckBox" in val.keys():
                    del val["checkCodeCheckBox"]
                    del val["checkFieldCheckBox"]

    def getRanFloatNum(self, lower, upper):
        return round(random.uniform(lower, upper), 2)

    def getRanIntNum(self, lower, upper):
        return int(random.uniform(lower, upper))

    def getBitsize(self, variable):
        '''
        @description: 根据变量的名称获取它的位大小
        @param {*} self
        @param {*} variable 变量的名称
        @return {*} 返回值是一个int类型的数值，表示了它占多少位
        '''
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

    def initStructDict(self, header_loc_list, seedJSONPath, readJSON, ui, struct, allStruct):
        """根据传入的路径分析头文件，或直接读取现有的json文件
        Parameters
        ----------
        header_loc_list : list
            列表，其中存储了所有头文件的位置
        seedJSONPath : str
            seed的JSON文件的存储路径
        readJSON : Bool
            是否读取已有的json
        ui : Ui_Dialog
            主界面的ui
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
        self.ui = ui
        global structDict
        structDict.clear()
        if readJSON:
            # 如果seedJSONPath是空字符串，表示用户没有选择JSON就按了右上角的X
            if seedJSONPath == "":
                return
            f = open(seedJSONPath, "r")
            structDict = json.load(f)
            f.close()
            self.struct = list(structDict.keys())[0]
        else:
            self.struct = struct
            # structInfo是一个List(tuple(name, loc)), 存储了可设置初始值的成员变量名称和它所在的位置
            structInfo = sa.getOneStruct(header_loc_list, struct, "", allStruct)
            typedefDict = sa.getTypedefDict(header_loc_list)
            # print(structInfo)
            tempDict = {}
            # 分析并设置structDict的值
            for i in range(0, len(structInfo)):
                tempDict[structInfo[i][0]] = {"value": None, "lower": 0, "upper": 999, "mutation": False, "bitsize": -1,
                                              "checkCode": False, "checkField": False}
                tempDict[structInfo[i][0]]["loc"] = structInfo[i][1]
                # 如果用户指定了位大小
                if ":" in structInfo[i][0]:
                    tempDict[structInfo[i][0]]["bitsize"] = int(structInfo[i][0].split(":")[1])
                    if "unsigned" in structInfo[i][0]:
                        tempDict[structInfo[i][0]]["upper"] = 2 ** tempDict[structInfo[i][0]]["bitsize"] - 1
                        tempDict[structInfo[i][0]]["lower"] = 0
                    else:
                        tempDict[structInfo[i][0]]["upper"] = 2 ** (tempDict[structInfo[i][0]]["bitsize"] - 1) - 1
                        tempDict[structInfo[i][0]]["lower"] = 0 - 2 ** (tempDict[structInfo[i][0]]["bitsize"] - 1)
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
                            tempDict[structInfo[i][0]
                                     ]["bitsize"] = dataTypeDict[dataType]["bitsize"]
                        tempDict[structInfo[i][0]]["upper"] = dataTypeDict[dataType]["upper"]
                        tempDict[structInfo[i][0]]["lower"] = dataTypeDict[dataType]["lower"]
                    except BaseException as e:
                        print("分析" + dataType + "类型时出错:", e)
                        tempDict[structInfo[i][0]]["upper"] = 999
                        tempDict[structInfo[i][0]]["lower"] = -999
            structDict[struct] = tempDict
        for k, v in structDict[self.struct].items():
            print(k)
            print(v)
        structDict = handle_struct(struct_dict=structDict)
        # 设置Table
        self.setTableContent()

    def initStructDictBySeedBinary(self, header_loc_list, seedBinaryPath, ui, struct, allStruct):
        """根据结构体格式与种子二进制的内容设置界面

        Parameters
        ----------
        header_loc_list : list
            头文件列表
        seedBinaryPath : str
            测试用例二进制文件路径
        ui : Ui_MainWindow
            主界面的ui
        struct : str
            所选结构体的名称
        allStruct : list
            全部结构体

        Notes
        -----
        [description]
        """
        self.header_loc_list = header_loc_list
        self.ui = ui
        global structDict
        structDict.clear()

        self.struct = struct
        # structInfo是一个List(tuple(name, loc)), 存储了可设置初始值的成员变量名称和它所在的位置
        structInfo = sa.getOneStruct(header_loc_list, struct, "", allStruct)
        typedefDict = sa.getTypedefDict(header_loc_list)
        root_loc = os.path.dirname(header_loc_list[0])
        seedBinaryName = os.path.basename(seedBinaryPath)
        seedVisualPath = os.path.join(root_loc, "in", seedBinaryName + "Visual.txt")  # 测试用例可视化路径

        tempDict = dict()
        # 分析并设置structDict的上下限与位
        for i in range(0, len(structInfo)):
            tempDict[structInfo[i][0]] = {"value": None, "lower": 0, "upper": 999, "mutation": False, "bitsize": -1,
                                            "checkCode": False, "checkField": False}
            tempDict[structInfo[i][0]]["loc"] = structInfo[i][1]
            # 如果用户指定了位大小
            if ":" in structInfo[i][0]:
                tempDict[structInfo[i][0]]["bitsize"] = int(structInfo[i][0].split(":")[1])
                if "unsigned" in structInfo[i][0]:
                    tempDict[structInfo[i][0]]["upper"] = 2 ** tempDict[structInfo[i][0]]["bitsize"] - 1
                    tempDict[structInfo[i][0]]["lower"] = 0
                else:
                    tempDict[structInfo[i][0]]["upper"] = 2 ** (tempDict[structInfo[i][0]]["bitsize"] - 1) - 1
                    tempDict[structInfo[i][0]]["lower"] = 0 - 2 ** (tempDict[structInfo[i][0]]["bitsize"] - 1)
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
                        tempDict[structInfo[i][0]
                                    ]["bitsize"] = dataTypeDict[dataType]["bitsize"]
                    tempDict[structInfo[i][0]]["upper"] = dataTypeDict[dataType]["upper"]
                    tempDict[structInfo[i][0]]["lower"] = dataTypeDict[dataType]["lower"]
                except BaseException as e:
                    print("分析" + dataType + "类型时出错:", e)
                    tempDict[structInfo[i][0]]["upper"] = 999
                    tempDict[structInfo[i][0]]["lower"] = -999
        structDict[struct] = tempDict

        # 生成C文件并编译为dll，然后调用
        public.genTestcaseVisual(header_loc_list, struct, structDict)
        cmd = "gcc -shared -o " + os.path.join(root_loc, "in", "testcaseVisual.dll ") + os.path.join(root_loc, "in", "testcaseVisual.c")
        os.system(cmd)
        visualDll = ctypes.cdll.LoadLibrary(os.path.join(root_loc, "in", "testcaseVisual.dll "))
        visualDll.testcaseVisualization(open(seedBinaryPath, mode="rb").read(), bytes(seedVisualPath, encoding="utf8"))
        seedValueDict = dict()
        with open(seedVisualPath) as f:
            lines = f.readlines()
            for line in lines:
                seedValueDict[line.split(":")[0]] = int(line.split(":")[1])
        for k, v in structDict[self.struct].items():
            v["value"] = 0  # 默认值是0
            dataName = k.split(" ")[-1].split(":")[0]
            if not dataName in seedValueDict:
                print("Not found")
            else:
                v["value"] = seedValueDict[dataName]
        _ctypes.FreeLibrary(visualDll._handle)      # 释放dll资源

        structDict = handle_struct(struct_dict=structDict)

        # 设置Table
        self.setTableContent()

    def genMutate(self):
        '''
        @description: 生成一个c文件，里面有变异的方法和将值设置在指定范围内的方法
        @param {*} self
        @return {*}
        '''
        global hasCheckCode
        for key in structDict:
            struct = key
        try:
            public.genMutate(self.header_loc_list, struct, structDict, self.checkCodeComboBox.currentText(),
                             hasCheckCode)
            print("mutate.c生成成功!")
        except BaseException as e:
            print("\033[1;31m")
            traceback.print_exc()
            print("\033[0m")

    def gen_check_code(self, structDict, struct):
        """
        根据字典中的字段，判断校验字段和校验值存放位置，计算校验值
        @param structDict:
        @param struct:
        @return:
        """
        check_code_value = []
        check_code_holder_name = 0
        for key, value in structDict[struct].items():
            if value["checkField"]:
                check_code_value.append(value["value"])
            elif value["checkCode"]:
                check_code_holder_name = key
        check_code_method = self.checkCodeComboBox.currentText()
        check_code = calculate_check_code_from_dec(dec_data_list=check_code_value,
                                                   method=check_code_method.split("_")[0],
                                                   algorithm=check_code_method.split("_")[1])
        if check_code_holder_name == 0 and len(check_code_value) == 0:
            print("没有指定校验码和校验字段，生成初始种子时不修改value")
            return (structDict, False)
        elif (check_code_holder_name == 0 and len(check_code_value) != 0) or (check_code_holder_name != 0 and len(
                check_code_value) == 0):
            print("校验码和校验字段应该同时设置，请至少设置一个校验字段和校验码位置，此处当均未设置处理")
            return (structDict, False)
        else:
            structDict[struct][check_code_holder_name]["value"] = check_code
            return (structDict, True)

    def genSeed(self):
        '''
        @description: 根据输入的内容，生成种子测试用例seed.txt
        @param {*} self
        @return {*}
        '''
        global structDict
        global hasCheckCode
        for key in structDict:
            struct = key
        structDict, hasCheckCode = self.gen_check_code(structDict, struct)  # 根据校验方法，计算校验值，并存放到structDict.value里，用于初始化种子
        public.genSeed(self.header_loc_list, struct, structDict, self.checkCodeComboBox.currentText(), hasCheckCode)
        # 生成变异所需的C文件
        try:
            # 生成变异所需C文件
            self.genMutate()
            # 将用户所选的结构体的分析结果保存为input.json
            root_loc = re.sub(self.header_loc_list[0].split("/")[-1], "", self.header_loc_list[0]) + "/in/"
            jsonFile = open(root_loc + "input.json", "w")
            self.delCheckBox()
            json.dump(structDict, jsonFile)
            jsonFile.close()
            self.setTableContent()
            check_code_method_save_file_path = root_loc + "checkCodeMethod.txt"
            check_code_method_save_file = open(check_code_method_save_file_path, mode="w", encoding="utf")
            check_code_method_save_file.write(self.checkCodeComboBox.currentText())
            check_code_method_save_file.close()
            genSeedMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, "消息", "种子文件生成成功!")
            genSeedMsgBox.exec_()
        except BaseException as e:
            genSeedMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "种子文件生成失败: " + str(e))
            genSeedMsgBox.exec_()
            traceback.print_exc()


    def setDataTypeDict(self, typeJSONPath):
        global dataTypeDict
        if not os.path.exists(typeJSONPath):
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
            return

        f = open(typeJSONPath)
        dataTypeDict = json.load(f)
        f.close()


    def setAllVariableMutate(self):
        global structDict
        for struct, vars in structDict.items():
            for key, val in vars.items():
                structDict[struct][key]["mutation"] = True
        self.setTableContent()


    def setAllVariableNotMutate(self):
        global structDict
        for struct, vars in structDict.items():
            for key, val in vars.items():
                structDict[struct][key]["mutation"] = False
        self.setTableContent()


    def setAllVariableCheckField(self):
        global structDict
        for struct, vars in structDict.items():
            for key, val in vars.items():
                structDict[struct][key]["checkField"] = True
                structDict[struct][key]["checkCode"] = False
        self.setTableContent()


    def setAllVariableNotCheckField(self):
        global structDict
        for struct, vars in structDict.items():
            for key, val in vars.items():
                structDict[struct][key]["checkField"] = False
        self.setTableContent()
    # 结束


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
