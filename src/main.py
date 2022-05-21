import json
import os

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, QRect, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QHeaderView, QStyleOptionButton, QStyle, QCheckBox, QFileDialog, \
    QTableWidgetItem

from src.common.setting import main_ui_path, header_field, conf_json, origin_conf

# 用来装行表头所有复选框 全局变量
from src.common.utils import sync_dict

all_header_combobox = []


class project_conf():
    def __init__(self):
        with open(conf_json, 'r', encoding='utf-8') as f:
            try:
                CONF_JSON = json.load(f)
                # 净化配置文件
                sync_dict(origin_conf, CONF_JSON)
            except Exception as e:
                print(e)
                CONF_JSON = self.reset()
            f.close()
        self.PROJECT_CONF = CONF_JSON
        self.updateConf()

    def reset(self):
        return origin_conf

    def updateConf(self):
        with open(conf_json, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.PROJECT_CONF))
            f.close()


class CheckBoxHeader(QHeaderView):
    """自定义表头类"""

    # 自定义 复选框全选信号
    select_all_clicked = Signal(bool)
    # 这4个变量控制列头复选框的样式，位置以及大小
    _x_offset = 0
    _y_offset = 0
    _width = 20
    _height = 20

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.isOn = False

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()

        self._y_offset = int((rect.height() - self._width) / 2.)

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + self._x_offset, rect.y() + self._y_offset, self._width, self._height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if 0 == index:
            x = self.sectionPosition(index)
            if x + self._x_offset < event.pos().x() < x + self._x_offset + self._width and self._y_offset < event.pos().y() < self._y_offset + self._height:
                if self.isOn:
                    self.isOn = False
                else:
                    self.isOn = True
                    # 当用户点击了行表头复选框，发射 自定义信号 select_all_clicked()
                self.select_all_clicked.emit(self.isOn)

                self.updateSection(0)
        super(CheckBoxHeader, self).mousePressEvent(event)

    # 自定义信号 select_all_clicked 的槽方法
    def change_state(self, isOn):
        # 如果行表头复选框为勾选状态
        if isOn:
            # 将所有的复选框都设为勾选状态
            for i in all_header_combobox:
                i.setCheckState(Qt.Checked)
        else:
            for i in all_header_combobox:
                i.setCheckState(Qt.Unchecked)


class Ui_Mainwindows():
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        print(main_ui_path)
        self.ui = QUiLoader().load(main_ui_path)
        # 创建设置对象
        global conf, path_conf, selected_files_list, recommended_constant
        conf = project_conf()
        path_conf = conf.PROJECT_CONF['path_conf']
        selected_files_list = conf.PROJECT_CONF['selected_files_list']
        recommended_constant = conf.PROJECT_CONF['recommended_constant']
        self.process()

    def process(self):
        # 载入配置文件
        self.syncConfigure()
        # pushButton连接
        self.signalConnect()
        # widgetInit状态初始化
        self.widgetInit()

    def syncConfigure(self):
        self.ui.lineEdit_export.setText(path_conf['export_path'])
        self.ui.lineEdit_filename.setText(recommended_constant['export_file_name'])

    def signalConnect(self):
        # 选择要合并的文件按钮
        self.ui.pushButton_add.clicked.connect(lambda: self.selectFiles())
        # 清空按钮
        self.ui.pushButton_clear.clicked.connect(lambda: self.clearTable())
        # 选择输出路径按钮
        self.ui.pushButton_export.clicked.connect(lambda: self.exportPath())
        # 开始合并按钮
        self.ui.pushButton_start.clicked.connect(lambda: self.startMerge())

    def widgetInit(self):
        # 设置表格
        self.setTableWidget()
        # # 开始合并按钮当没有文件选择时候设置禁用
        # self.ui.pushButton_start.setEnabled(False)
        # 输出路径
        self.ui.lineEdit_export.setFocusPolicy(Qt.NoFocus)  # 禁止编辑

    # 设置表格
    def setTableWidget(self):
        self.ui.tableWidget_selected.setColumnCount(len(header_field))  # 设置列数
        for i in range(len(header_field) - 1):
            # header_item = QTableWidgetItem(header_field[i])
            checkbox = QCheckBox()
            # 将所有的复选框都添加到 全局变量 all_header_combobox 中
            all_header_combobox.append(checkbox)
            # 为每一行添加复选框
            self.ui.tableWidget_selected.setCellWidget(i, 0, checkbox)

        header = CheckBoxHeader()  # 实例化自定义表头
        self.ui.tableWidget_selected.setHorizontalHeader(header)  # 设置表头
        self.ui.tableWidget_selected.setHorizontalHeaderLabels(header_field)  # 设置行表头字段

        header.select_all_clicked.connect(header.change_state)  # 行表头复选框单击信号与槽
        # 设置表头自适应大小
        self.ui.tableWidget_selected.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget_selected.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.ui.tableWidget_selected.setColumnWidth(0, 400)  # 设置第0列宽度
        self.ui.tableWidget_selected.setAlternatingRowColors(True)  # 交替行颜色
        # 刷新表格
        self.refreshTable()

    def selectFiles(self):
        file_names = QFileDialog.getOpenFileNames(self.ui, "选择路径", path_conf['last_work_path'],
                                                  'pdf file(*.pdf)')
        try:
            # 文件路径转换为文件夹路径
            work_path = file_names[0][0].split('/')
            work_path.pop(-1)
            work_path = '/'.join(work_path)
            # print(work_path)
            selected_files_list.clear()
            for f in file_names[0]:
                temp = {
                    'slected': False,
                    'path': f,
                    'file_name': f.split('/')[-1],
                    'page_num': PdfFileReader(f, strict=False).getNumPages()
                }
                # print(os.path.splitext(f)) #('E:/mysql/练习/章节练习/第01章_数据库概述', '.pdf')
                if os.path.splitext(f)[1] == '.pdf':
                    selected_files_list.append(temp)

            # 记忆工作路径
            path_conf['last_work_path'] = work_path
            # 设置推荐文件名
            if recommended_constant['export_file_name'] == '':
                recommended_constant['export_file_name'] = '输出的pdf'
            conf.updateConf()
            self.refreshTable()
            self.syncConfigure()
        except:
            print("未选文件")

    def refreshTable(self):
        self.clearTable()
        for w in selected_files_list:
            row_cnt = self.ui.tableWidget_selected.rowCount()
            self.ui.tableWidget_selected.insertRow(row_cnt)
            column_cnt = self.ui.tableWidget_selected.columnCount()
            # 添加数据
            check = QtWidgets.QCheckBox()
            check.setText(w['file_name'])  # 文字
            check.setEnabled(True)  # 不能修改
            check.setCheckState(Qt.Checked)  # 默认非选中
            self.ui.tableWidget_selected.setCellWidget(row_cnt, 0, check)
            # print(self.ui.tableWidget_selected.item(row_cnt,0).checkState())
            for column in range(1, column_cnt):
                item = QTableWidgetItem(str(w['page_num']))
                self.ui.tableWidget_selected.setItem(row_cnt, column, item)

    # 清空表格内容
    def clearTable(self):
        self.ui.tableWidget_selected.setRowCount(0)

    def exportPath(self):
        export_path = QFileDialog.getExistingDirectory(self.ui, "选择输出路径")
        # print(export_path)
        path_conf['export_path'] = export_path
        conf.updateConf()
        self.syncConfigure()

    def startMerge(self):
        filename = self.ui.lineEdit_filename.text()
        exportpath = self.ui.lineEdit_export.text() + '/'  + filename + '.pdf'
        mergePDF(exportpath)


def mergePDF(exportpath):
    merger = PdfFileMerger(strict=False)
    for s in selected_files_list:
        pdf = s['path']
        file_read = PdfFileReader(pdf, strict=False)
        page_num = file_read.getNumPages()
        if file_read.isEncrypted == True:
            print("不支持加密文件")
        else:
            merger.append(open(pdf, 'rb'))
    with open(exportpath, 'wb') as f:
        merger.write(f)



def main():
    app = QApplication([])
    mainwindow = Ui_Mainwindows()
    print("显示窗口")
    mainwindow.ui.show()
    app.exec_()


if __name__ == '__main__':
    main()
