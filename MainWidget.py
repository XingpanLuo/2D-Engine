
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PaintBoard import PaintBoard
"""
# 重要参考、引用说明
#  PyQt5基础学习：https://maicss.gitbooks.io/pyqt5/content/
#  PyQt5 布局参考学习(layout):https://zhuanlan.zhihu.com/p/64574283

"""
class MainWidget(QMainWindow):

    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.InitData() #先初始化数据，再初始化界面
        self.InitMenu()
        self.InitWidget()

    def InitData(self):
        self.shape_mode='line'
        self.__colorList = QColor.colorNames() 
        self.__paintBoard = PaintBoard(self)
        self.__button=Button(self.__paintBoard)
        self.__stateUI=self.InitStateUI()
        
    def InitMenu(self):              
        exitAction = QAction(QIcon('./icon/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)

    def InitWidget(self):
        self.resize(1920,1080)
        self.setWindowTitle("2D Physics Engine")
        
        low_layout=QHBoxLayout()
        low_layout.addWidget(self.__stateUI)
        low_layout.addWidget(self.__paintBoard)
        low_layout.setStretch(0,1)
        low_layout.setStretch(1,10)
        low_widget=QWidget()
        low_widget.setLayout(low_layout)

        upper_widget=self.__button

        main_layout=QVBoxLayout()
        main_layout.addWidget(upper_widget)
        main_layout.addWidget(low_widget)
        main_layout.setStretch(0,1)
        main_layout.setStretch(1,10)

        main_widget=QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


    def InitStateUI(self):
        sub_layout = QVBoxLayout()

        self.__btn_Update=QPushButton("模拟",self)
        self.__btn_Update.clicked.connect(self.__paintBoard.Update)
        sub_layout.addWidget(self.__btn_Update)

        self.__btn_Clear = QPushButton("清空画板",self)
        self.__btn_Clear.clicked.connect(self.__paintBoard.Clear)
        sub_layout.addWidget(self.__btn_Clear)

        self.__btn_Quit = QPushButton("退出",self)
        self.__btn_Quit.clicked.connect(self.Quit)
        sub_layout.addWidget(self.__btn_Quit)

        self.__btn_Save = QPushButton("保存作品")
        self.__btn_Save.setParent(self)
        self.__btn_Save.clicked.connect(self.on_btn_Save_Clicked)
        sub_layout.addWidget(self.__btn_Save)
        
        self.__label_penThickness = QLabel(self)
        self.__label_penThickness.setText("画笔粗细")
        self.__label_penThickness.setFixedHeight(20)
        sub_layout.addWidget(self.__label_penThickness)
        
        self.__spinBox_penThickness = QSpinBox(self)
        self.__spinBox_penThickness.setMaximum(20)
        self.__spinBox_penThickness.setMinimum(2)
        self.__spinBox_penThickness.setValue(3) #默认粗细为10
        self.__spinBox_penThickness.setSingleStep(2) #最小变化值为2
        self.__spinBox_penThickness.valueChanged.connect(self.on_PenThicknessChange)#关联spinBox值变化信号和函数on_PenThicknessChange
        sub_layout.addWidget(self.__spinBox_penThickness)
        
        self.__label_penColor = QLabel(self)
        self.__label_penColor.setText("画笔颜色")
        self.__label_penColor.setFixedHeight(20)
        sub_layout.addWidget(self.__label_penColor)
        
        self.__comboBox_penColor = QComboBox(self)
        self.__fillColorList(self.__comboBox_penColor) #用各种颜色填充下拉列表
        self.__comboBox_penColor.currentIndexChanged.connect(self.on_PenColorChange) #关联下拉列表的当前索引变更信号与函数on_PenColorChange
        sub_layout.addWidget(self.__comboBox_penColor)

        sub_layout.addStretch(0)

        sub_widget=QWidget()
        sub_widget.setLayout(sub_layout)
        return sub_widget


    def __fillColorList(self, comboBox):

        index_black = 0
        index = 0
        for color in self.__colorList: 
            if color == QColor(0,255,255):
                index_black = index
            index += 1
            pix = QPixmap(70,20)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix),None)
            comboBox.setIconSize(QSize(70,20))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        comboBox.setCurrentIndex(index_black)
        
    def on_PenColorChange(self):
        color_index = self.__comboBox_penColor.currentIndex()
        color_str = self.__colorList[color_index]
        self.__paintBoard.ChangePenColor(color_str)

    def on_PenThicknessChange(self):
        penThickness = self.__spinBox_penThickness.value()
        self.__paintBoard.ChangePenThickness(penThickness)
    
    def on_btn_Save_Clicked(self):
        savePath = QFileDialog.getSaveFileName(self, 'Save Your Paint', '.\\', '*.png')
        print(savePath)
        if savePath[0] == "":
            print("Save cancel")
            return
        image = self.__paintBoard.GetContentAsQImage()
        image.save(savePath[0])
        
        
        
    def Quit(self):
        self.close()



class Button(QWidget):
    def __init__(self,board=None):
        super().__init__()
        self.Parent=board
        # 创建水平布局
        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 0, 0, 0)  # 设置水平布局在Widget内上下左右的间距
        self.hLayout.setSpacing(10)  # 设置间距
        self.hLayout.setDirection(0)  # 自左向右的布局
        self.hLayout.addSpacing(10)  # 左侧空隙
        self.font = QFont()
        self.font.setFamily("黑体")
        self.font.setBold(1)  # 设置为粗体
        self.font.setPixelSize(24)  # 字体大小

        # 创建直线图像按钮
        self.btn_a1 = QPushButton() # 创建按钮
        self.btn_a1.setStyleSheet("QPushButton{color:white;background-color:rgb(45,45,45);font-family:黑体;}"
                                      "QPushButton:pressed{background-color:rgb(30,30,30)}")
        self.btn_a1.setFont(self.font)
        self.btn_a1.setText("地板")
        self.btn_a1.setFixedHeight(50)
        self.btn_a1.setFixedWidth(120)
        self.btn_a1.setParent(self)
        #self.btn_a1.setCheckable(True)
        self.btn_a1.clicked.connect(self.slot_a1)
        self.hLayout.addWidget(self.btn_a1)

        # 创建多边形按钮图标
        self.btn_a2 = QPushButton()
        self.btn_a2.setStyleSheet("QPushButton{color:white;background-color:rgb(45,45,45);font-family:黑体;}"
                                      "QPushButton:pressed{background-color:rgb(30,30,30)}")
        self.btn_a2.setFont(self.font)
        self.btn_a2.setText("多边形")
        self.btn_a2.setFixedHeight(50)
        self.btn_a2.setFixedWidth(120)
        self.btn_a2.setParent(self)
        #self.btn_a2.setCheckable(True)
        self.btn_a2.clicked.connect(self.slot_a2)
        self.hLayout.addWidget(self.btn_a2)

        # 创建图标
        self.btn_a3 = QPushButton()
        self.btn_a3.setStyleSheet("QPushButton{color:white;background-color:rgb(45,45,45);font-family:黑体;}"
                                      "QPushButton:pressed{background-color:rgb(30,30,30)}")
        self.btn_a3.setFont(self.font)
        self.btn_a3.setText("矩形")
        self.btn_a3.setFixedHeight(50)
        self.btn_a3.setFixedWidth(120)
        self.btn_a3.setParent(self)
        #self.btn_a3.setCheckable(True)
        self.btn_a3.clicked.connect(self.slot_a3)
        self.hLayout.addWidget(self.btn_a3)

        # 创建按钮
        self.btn_a4 = QPushButton()
        self.btn_a4.setStyleSheet("QPushButton{color:white;background-color:rgb(45,45,45);font-family:黑体;}"
                                      "QPushButton:pressed{background-color:rgb(30,30,30)}")
        self.btn_a4.setFont(self.font)
        self.btn_a4.setText("斜距形")
        self.btn_a4.setFixedHeight(50)
        self.btn_a4.setFixedWidth(120)
        self.btn_a4.setParent(self)
        self.btn_a4.clicked.connect(self.slot_a4)
        self.hLayout.addWidget(self.btn_a4)

        # 创建按钮
        self.btn_a5 = QPushButton() 
        self.btn_a5.setStyleSheet("QPushButton{color:white;background-color:rgb(45,45,45);font-family:黑体;}"
                                      "QPushButton:pressed{background-color:rgb(30,30,30)}")
        self.btn_a5.setFont(self.font)
        self.btn_a5.setText("圆形")
        self.btn_a5.setFixedHeight(50)
        self.btn_a5.setFixedWidth(120)
        self.btn_a5.setParent(self)
        self.btn_a5.clicked.connect(self.slot_a5)
        self.hLayout.addWidget(self.btn_a5)

        # 最后，在尾端添加弹簧，以至于布局呈现靠左而不是居中
        self.hLayout.addStretch()

    def slot_a1(self):
        self.Parent.shape_mode='line'
        print("set_shape_mode:line ")

    def slot_a2(self):
        self.Parent.shape_mode='poly'
        print("set_shape_mode:poly ")

    def slot_a3(self):
        self.Parent.shape_mode='rect'
        print("set_shape_mode:rect ")

    def slot_a4(self):
        self.Parent.shape_mode='srect'
        print("set_shape_mode:srect")

    def slot_a5(self):
        self.Parent.shape_mode='circ'
        print("set_shape_mode:circ ")
