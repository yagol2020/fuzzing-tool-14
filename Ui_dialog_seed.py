'''
Author: 金昊宸
Date: 2021-04-22 14:26:43
LastEditTime: 2021-07-20 21:15:44
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
            "instrument": False,
            "mutation": False,
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
# 其中存储了数据类型和它对应的位
dataBitsizeDict = {
    "_Bool": 8,
    "char": 8,
    "int": 32,
    "short": 16,
    "unsigned char": 8,
    "unsigned short": 16,
    "unsigned int": 32,
    "float": 32,
    "double": 64
}
# 数据类型字典-end

# 数据类型上下限字典-start
dataRangeDict = {
    "_Bool": {"lower": 0, "upper": 1},
    "char": {"lower": -128, "upper": 127},
    "int": {"lower": 0 - 2 ** 31, "upper": 2 ** 31 - 1},
    "short": {"lower": 0 - 2 ** 15, "upper": 2 ** 15 - 1},
    "unsigned char": {"lower": 0, "upper": 2 ** 8 - 1},
    "unsigned short": {"lower": 0, "upper": 2 ** 16 - 1},
    "unsigned int": {"lower": 0, "upper": 2 ** 32 - 1},
    # TODO float和double的上下限太大了，看起来很长，所以暂时设置成了int的上下限
    "float": {"lower": float(0 - 2 ** 31), "upper": float(2 ** 31 - 1)},
    "double": {"lower": float(0 - 2 ** 31), "upper": float(2 ** 31 - 1)}
}


# 数据类型上下限字典-end

# TODO 改为报文输入的结构

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        global structDict
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("自定义结构体成员变量值")
        Dialog.resize(1500, 550)
        self.setTable(Dialog)

    def setTable(self, Dialog):  # 界面函数
        global structDict

        # 表格-start
        self.structTable = QtWidgets.QTableWidget(Dialog)
        self.structTable.setGeometry(QtCore.QRect(10, 10, 880, 480))
        self.structTable.setColumnCount(9)
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
        self.generateBtn.setText("生成种子文件")
        self.generateBtn.clicked.connect(self.genSeed)
        # self.generateBtn.clicked.connect(Dialog.accept)
        # 生成按钮-end

        # 下拉菜单选择校验算法-start
        self.checkCodeComboBox = QtWidgets.QComboBox(Dialog)
        self.checkCodeComboBox.setGeometry(QtCore.QRect(1000, 10, 91, 31))
        self.checkCodeComboBox.setObjectName("checkCodeComboBox")
        # 添加项目
        check_code_methods = get_support_methods()
        for index in range(len(check_code_methods)):
            self.checkCodeComboBox.addItem("")
            self.checkCodeComboBox.setItemText(index, check_code_methods[index])
        # 下拉菜单选择校验算法-end

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
        self.structTable.setHorizontalHeaderLabels(
            ['结构体', '成员变量', '当前值', '范围下限', "范围上限", "位", "注释", "是否为插装变量", "是否变异"])

        i = 0  # 行
        j = 0  # 列
        self.insCheckBoxItemDict = structDict  # 插装变量复选框的字典
        # 不可编辑的item
        for key, val in structDict.items():
            structKey = key  # 结构体名
            for key, val in val.items():
                self.structTable.setItem(
                    i, 0, self.enableeditItem(structKey))  # 结构体名
                self.structTable.setItem(
                    i, 1, self.enableeditItem(key))  # 成员变量名
                # if val['value']==None:
                #     structDict[structKey][key]['value'] = self.getRanNum(
                #         val['lower'], val['upper'])
                self.structTable.setCellWidget(
                    i, 2, self.lineEditItem(True, val['value'], 'value', structKey, key))  # 当前值
                self.structTable.setCellWidget(
                    i, 3, self.lineEditItem(True, val['lower'], 'lower', structKey, key))  # 下限
                self.structTable.setCellWidget(
                    i, 4, self.lineEditItem(True, val['upper'], 'upper', structKey, key))  # 上限
                self.structTable.setItem(
                    i, 5, self.enableeditItem(str(val["bitsize"])))  # 位
                self.structTable.setItem(
                    i, 6, self.enableeditItem(str(val["comment"])))  # 注释
                self.structTable.setCellWidget(
                    i, 7, self.insCheckBoxItem(val['instrument'], structKey, key))  # 插装
                self.structTable.setCellWidget(
                    i, 8, self.varCheckBoxItem(val['mutation'], structKey, key))  # 变异
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
        # self.insCheckBoxItemDict[struct][memVal]['checkBox'] = checkBox
        return checkBox

    def varCheckChange(self, checkBool, struct, memVal):  # CheckBox修改函数
        global structDict
        # for key, val in structDict.items():
        #     for key, val in val.items():
        #         val['instrument'] = checkBool
        structDict[struct][memVal]['mutation'] = checkBool

    # 表格变异-CheckBox-end

    # 表格插装变量-CheckBox-start
    def insCheckBoxItem(self, checkBool, struct, memVal):
        global structDict
        checkBox = QtWidgets.QCheckBox()
        checkBox.setChecked(checkBool)
        checkBox.stateChanged.connect(
            lambda: self.insCheckChange(checkBox.isChecked(), struct, memVal))
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

    # 表格插装变量-CheckBox-end

    # 表格-LineEdit-start
    def lineEditItem(self, isNumber, placeholderText, whatThing, struct, memVal):
        global structDict
        lineEdit = QtWidgets.QLineEdit()
        # print(isNumber, placeholderText, whatThing, struct, memVal)
        if isNumber:
            # 输入框文本验证-start
            reg = QRegExp('^(\-|\+)?\d+(\.\d+)?$')  # 正数、负数、小数-正则
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
                structDict[struct][memVal]['value'] = self.getRanFloatNum(
                    structDict[struct][memVal]['lower'], structDict[struct][memVal]['upper'])
                lineEdit.setPlaceholderText(
                    "随机值(%.2f)" % structDict[struct][memVal]['value'])  # 浮点型默认文字
            else:
                structDict[struct][memVal]['value'] = self.getRanIntNum(
                    structDict[struct][memVal]['lower'], structDict[struct][memVal]['upper'])
                lineEdit.setPlaceholderText(
                    "随机值(%d)" % structDict[struct][memVal]['value'])  # 整型默认文字
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
                maxUpper = dataRangeDict[dataType]["upper"]
                minLower = dataRangeDict[dataType]["lower"]
        except BaseException as e:
            print("获取上下限时出错:", e, "将默认为int的上下限\033[1;31m")
            traceback.print_exec()
            print("\033[0m")

        dataType = memVal.split(" ")
        dataType.pop(-1)
        dataType = " ".join(dataType)
        # 如果编辑的是值的内容
        if text != "" and whatThing == 'value':
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
                    QMessageBox.Warning, '错误',
                    '请输入%s-%s内的值' % (structDict[struct][memVal]["lower"], structDict[struct][memVal]["upper"]))
                msg_box.exec_()
                lineEdit.clear()
                # 超范围错误提醒-end

        outOfRangeBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "警告", "设置的值超出范围，有溢出风险!")
        # 如果编辑的是下限的内容
        if whatThing == 'lower':
            if float(text) < minLower or float(text) > maxUpper:
                outOfRangeBox.exec_()
                lineEdit.clear()
            else:
                if "float" in dataType or "double" in dataType:
                    structDict[struct][memVal][whatThing] = float(text)
                else:
                    structDict[struct][memVal][whatThing] = int(text)

        # 如果编辑的是上限的内容
        if whatThing == 'upper':
            if float(text) < minLower or float(text) > maxUpper:
                lineEdit.clear()
                outOfRangeBox.exec_()
            else:
                if "float" in dataType or "double" in dataType:
                    structDict[struct][memVal][whatThing] = float(text)
                else:
                    structDict[struct][memVal][whatThing] = int(text)

    '''
    @description: 将strctDict保存为JSON文件
    @param {*} self
    @return {*}
    '''

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
            self.setTableContent(structDict)
            # 弹出保存成功的消息框
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, "消息", "保存成功!")
            saveMsgBox.exec_()
        except BaseException as e:
            traceback.print_exc()
            saveMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "保存失败!\n" + repr(e))
            saveMsgBox.exec_()

    def delCheckBox(self):  # 清空字典中delcheckbox
        global structDict
        for key, val in structDict.items():
            for key, val in val.items():
                if 'checkBox' in val.keys():
                    del val['checkBox']

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
            for key, value in dataBitsizeDict.items():
                if key == dataType:
                    return value
            return -1

    def initStructDict(self, header_loc_list, JSONPath, readJSON, struct, allStruct):
        """根据传入的路径分析头文件，或直接读取现有的json文件
        Parameters
        ----------
        header_loc_list : list
            列表，其中存储了所有头文件的位置
        JSONPath : str
            JSON文件的存储路径
        readJSON : Bool
            是否读取已有的json
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
        global structDict
        structDict.clear()
        if readJSON:
            # 如果JSONPath是空字符串，表示用户没有选择JSON就按了右上角的X
            if JSONPath == "":
                return
            f = open(JSONPath, "r")
            structDict = json.load(f)
            f.close()
        else:
            # structInfo是一个List(tuple(name, loc)), 存储了可设置初始值的成员变量名称和它所在的位置
            structInfo = sa.getOneStruct(header_loc_list, struct, "", allStruct)
            print(structInfo)
            tempDict = {}
            # 分析并设置structDict的值
            for i in range(0, len(structInfo)):
                tempDict[structInfo[i][0]] = {"value": None, "lower": 0, "upper": 999, "instrument": False,
                                              "mutation": False, "bitsize": 8}
                tempDict[structInfo[i][0]]["bitsize"] = self.getBitsize(structInfo[i][0])
                tempDict[structInfo[i][0]]["loc"] = structInfo[i][1]
                # 如果用户指定了位大小
                if ":" in structInfo[i][0]:
                    if "unsigned" in structInfo[i][0]:
                        tempDict[structInfo[i][0]]["upper"] = 2 ** tempDict[structInfo[i][0]]["bitsize"] - 1
                        tempDict[structInfo[i][0]]["lower"] = 0
                    else:
                        tempDict[structInfo[i][0]]["upper"] = 2 ** (tempDict[structInfo[i][0]]["bitsize"] - 1) - 1
                        tempDict[structInfo[i][0]]["lower"] = 0 - (2 ** tempDict[structInfo[i][0]]["bitsize"] - 1)
                else:
                    # 如果用户没指定位大小，自动获取
                    # dataType: 表示数据类型，从list变为str
                    dataType = structInfo[i][0].split(" ")
                    dataType.pop(-1)
                    dataType = " ".join(dataType)
                    try:
                        tempDict[structInfo[i][0]]["upper"] = dataRangeDict[dataType]["upper"]
                        tempDict[structInfo[i][0]]["lower"] = dataRangeDict[dataType]["lower"]
                    except BaseException as e:
                        print("分析" + dataType + "类型时出错:", e)
                        tempDict[structInfo[i][0]]["upper"] = 999
                        tempDict[structInfo[i][0]]["lower"] = -999
            structDict[struct] = tempDict
        structDict = handle_struct(struct_dict=structDict)
        # 设置Table
        print(structDict)
        self.setTableContent(structDict)

    def genMutate(self):
        '''
        @description: 生成一个c文件，里面有变异的方法、获取插装值的方法和将值设置在指定范围内的方法
        @param {*} self
        @return {*}
        '''
        for key in structDict:
            struct = key
        try:
            public.genMutate(self.header_loc_list, struct, structDict)
            print("mutate_instru.c生成成功!")
        except BaseException as e:
            print("mutate_instru.c生成失败: ", e)

    def genInstrument(self):
        '''
        @description: 将插桩的变量写入instrument.txt
        @param {*} self
        @return {*}
        '''
        for key in structDict:
            struct = key
        # 查看哪个变量是插桩变量
        try:
            for key, value in structDict[struct].items():
                if value["instrument"]:
                    instrumentFile = open(
                        re.sub(self.header_loc_list[0].split(
                            "/")[-1], "", self.header_loc_list[0]) + "in/instrument.txt",
                        mode="w")
                    instrumentFile.write(key)
                    instrumentFile.close()
                    break
            print("instrument.txt保存成功!")
        except:
            print("instrument.txt保存失败!")

    def gen_check_code(self, structDict, struct):
        check_code_value = []
        check_code_holder_name = 0
        for key, value in structDict[struct].items():
            if value["checkCode"] == "should":
                check_code_value.append(value["value"])
            elif value["checkCode"] == "holder":
                check_code_holder_name = key
        check_code_method = self.checkCodeComboBox.currentText()
        check_code = calculate_check_code_from_dec(dec_data_list=check_code_value,
                                                   method=check_code_method.split(":")[0],
                                                   algorithm=check_code_method.split(":")[1])
        structDict[struct][check_code_holder_name]["value"] = check_code
        return structDict

    def genSeed(self):
        '''
        @description: 根据输入的内容，生成种子测试用例seed.txt
        @param {*} self
        @return {*}
        '''
        for key in structDict:
            struct = key
        # TODO 使用校验码
        # structDict = self.gen_check_code(structDict, struct)  # 根据校验方法，计算校验值，并存放到structDict.value里
        public.genSeed(self.header_loc_list, struct, structDict)
        # 生成变异所需得dll文件和表示插桩变量的txt
        try:
            self.genMutate()
            self.genInstrument()
            genSeedMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information, "消息", "种子文件生成成功!")
        except:
            genSeedMsgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, "警告", "种子文件生成失败!")
        genSeedMsgBox.exec_()
    # 结束


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     headerNotExistBox = QtWidgets.QMessageBox(
#         QtWidgets.QMessageBox.Information, "消息", "请运行Ui_window.py :)")
#     headerNotExistBox.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())