
import imp
import time
from tkinter.messagebox import NO
from turtle import update 
from PyQt5.QtWidgets import QWidget,QApplication
from PyQt5.Qt import QPixmap, QPainter, QPointF,QColor, QSize 
from PyQt5.QtCore import Qt
from Shape import *
from Engine import *
class PaintBoard(QWidget):
    def __init__(self, Parent=None):
        super().__init__(Parent)

        self.__InitData() #先初始化数据，再初始化界面
        self.__InitView()
        
    def __InitData(self):
        
        self.__size = QSize(480*3,560*3)
        """
        (0,0)   (1440,0)
        (0,825) (1440,825)
        (0,1430)    (1440,1630)
        """
        #新建QPixmap作为画板，尺寸为__size
        self.__board = QPixmap(self.__size)
        self.__board.fill(Qt.black) #用黑色填充画板
        
        self.__IsEmpty = True #默认为空画板 
        self.EraserMode = False #默认为禁用橡皮擦模式
        
        self.start = QPointF(0,0)#上一次鼠标位置
        self.end = QPointF(0,0)#当前的鼠标位置
        
        self.__painter = QPainter()#新建绘图工具
        
        self.width = 3       #默认画笔粗细为10px
        self.color = QColor(0,191,255)#设置默认画笔颜色
        #self.__colorList = QColor.colorNames() #获取颜色列表

        self.isPressed=False
        self.shape_mode='line'
        self.polygon_stop=True
        self.shape_list=[]
        self.history_list=[]
        self.body_list=[]
        self.shape=None
        self.body=None 
        self.myUpdate=False
        self.id=0

        self.engine=Engine()


    def Update(self):
        self.myUpdate=not self.myUpdate
        self.engine.sat.board=self 
        while(self.myUpdate):
            QApplication.processEvents()
            self.engine.run()
            self.bodyToShape()
            self.update()

    def __InitView(self):
        print("make_shape:line")
        self.shape=Line(self)
        self.shape.set_start(QPointF(25,1600))
        self.shape.set_end(QPointF(1380,1600))
        self.shape.calc_polygon()
        self.update()

        self.shape_list.append(self.shape)
        self.id=0
        self.shapeToBody(self.shape)
        self.shape=None
        #设置界面的尺寸为__size
        #self.setFixedSize(self.__size)
        
    def Clear(self):
        #清空画板
        self.__board.fill(Qt.black)
        self.history_list=self.shape_list
        del self.shape_list[1:]
        del self.body_list[1:]
        del self.engine.body_list[1:]
        self.id=1
        # self.shape_list.clear()
        # self.body_list.clear()
        

        self.update()
        self.__IsEmpty = True
        
    def ChangePenColor(self, color=QColor(0,191,255)):
        #改变画笔颜色
        self.color = QColor(color)
        
    def ChangePenThickness(self, thickness=3):
        #改变画笔粗细
        self.width = thickness
        
    def IsEmpty(self):
        #返回画板是否为空
        return self.__IsEmpty
    
    def GetContentAsQImage(self):
        #获取画板内容（返回QImage）
        image = self.__board.toImage()
        return image
        
    def shapeToBody(self,s):
        #for s in self.shape_list:
            self.body=Body()
            self.body.mode=s.shape_mode
            if s.shape_mode=='line':
                self.body.mode='line'
                self.body.points_list=s.points_list.copy()
            elif s.shape_mode=='poly' or s.shape_mode=='srect':
                self.body.points_list=(s.points_list).copy()
            elif s.shape_mode=='rect':
                p1=s.start
                p3=s.end
                p2=QPointF(p3.x(),p1.y())
                p4=QPointF(p1.x(),p3.y())
                self.body.points_list=[p1,p2,p3,p4]
            elif s.shape_mode=='circ':
                self.body.center=s.start
                self.body.end=s.end
                self.body.radius=s.radius
                self.body.points_list.append(s.start)
            self.body.id=self.id
            self.id=self.id+1
            self.body_list.append(self.body)
            self.engine.body_list.append(self.body)
            self.body=None

    def bodyToShape(self):
        l=len(self.shape_list)
        for i in range(0,len(self.body_list)):
            if i>=l:
                return 
            s=self.shape_list[i]
            b=self.body_list[i]
            if(s.shape_mode!=b.mode):
                print("s.shape:",s.shape_mode," b.shape:",b.mode," error")
                print("shape:",self.shape_list,"body:",self.body_list)
                return 
            if s.shape_mode=='line':
                s.start=b.points_list[0]
                s.end=b.points_list[1]
            elif s.shape_mode=='poly' or s.shape_mode=='srect':
                s.points_list=(b.points_list).copy()
                s.coll_points_list=(b.coll_points_list).copy()
                s.coll_axes_list=(b.coll_axes_list).copy()
                s.rect=True
            elif s.shape_mode=='rect':
                s.start=b.points_list[0]
                s.end=b.points_list[2]
                s.points_list=(b.points_list).copy()
                s.coll_points_list=(b.coll_points_list).copy()
                s.coll_axes_list=(b.coll_axes_list).copy()
            elif s.shape_mode=='circ':
                s.start=b.center
                s.end=b.end
                s.radius=b.radius 
                s.coll_points_list=(b.coll_points_list).copy()
                s.coll_axes_list=(b.coll_axes_list).copy()

    def paintEvent(self, paintEvent):
        #绘图事件
        #绘图时必须使用QPainter的实例，此处为__painter
        #绘图在begin()函数与end()函数间进行
        #begin(param)的参数要指定绘图设备，即把图画在哪里
        #drawPixmap用于绘制QPixmap类型的对象
        self.__painter.begin(self)
        # 0,0为绘图的左上角起点的坐标，__board即要绘制的图
        self.__painter.drawPixmap(0,0,self.__board)
        self.__painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        #self.Clear()
        for i in range(0,len(self.shape_list)):
            self.shape_list[i].draw(self.__painter)
        if(self.shape!=None):
            self.shape.draw(self.__painter)
        self.__painter.end()

    def mousePressEvent(self, mouseEvent):
        #鼠标按下时，获取鼠标的当前位置保存为上一次位置
        self.isPressed=True
        self.end =  mouseEvent.pos()
        self.start = self.end
        #print(self.start)
        if(self.shape_mode=='line'):
            if(Qt.LeftButton==mouseEvent.button()):
                print("make_shape:line")
                self.shape=Line(self)
        elif(self.shape_mode=='rect'):
            if(Qt.LeftButton==mouseEvent.button()):
                print("make_shape:rect")
                self.shape=Rect(self)
        elif(self.shape_mode=='circ'):
            if(Qt.LeftButton==mouseEvent.button()):
                print("make_shape:circ")
                self.shape=Circ(self)
        elif(self.shape_mode=='poly'):
            if(Qt.LeftButton==mouseEvent.button()):
                if(self.shape==None):
                    self.shape=Poly(self)
                    print("make_shape:poly")
                    self.shape.points_list.append(self.start)
                    self.shape.addNum()
            elif(Qt.RightButton==mouseEvent.button()):
                if(self.shape!=None):
                    self.shape.points_list.append(self.end)
                    self.shape.addNum()
        elif(self.shape_mode=='srect'):
            if(Qt.LeftButton==mouseEvent.button()):
                if(self.shape==None):
                    self.shape=SRect(self)
                    print("make_shape:srect")
                    self.shape.points_list.append(mouseEvent.pos())
                    self.shape.count=1
            elif(Qt.RightButton==mouseEvent.button()):
                if(self.shape!=None):
                    if(self.shape.count>=1):
                        self.shape.points_list[1]=mouseEvent.pos()
                        self.shape.count=2

        if(self.shape != None):
            self.shape.set_start(self.start)
            self.shape.set_end(self.end)
        try:
            self.update()
        except:
            pass 
        
        
    def mouseMoveEvent(self, mouseEvent):
        #鼠标移动时，更新当前位置，并在上一个位置和当前位置间画线
        self.end =  mouseEvent.pos()
        # self.__painter.begin(self.__board)
        
        # if self.EraserMode == False:
        #     #非橡皮擦模式
        #     self.__painter.setPen(QPen(self.color,self.__thickness,Qt.SolidLine,Qt.RoundCap)) #设置画笔颜色，粗细
        # else:
        #     #橡皮擦模式下画笔为纯白色，粗细为10
        #     self.__painter.setPen(QPen(Qt.white,10))
        # # self.__painter.setRenderHint(QPainter.Antialiasing)
        # # path = QPainterPath()
        # # path.moveTo(self.start)
        # # mid=self.start+(self.end-self.start)/2.0
        # # path.cubicTo(self.start, mid , self.end)
        # # self.__painter.drawPath(path)  

        # self.__painter.end()
        if(self.isPressed and self.shape!=None):
            self.shape.set_end(self.end)
            if(self.shape.shape_mode=='poly'):
                l=len(self.shape.points_list)
                if(l<self.shape.point_nums+1):
                    self.shape.points_list.append(self.end)
                else:
                    self.shape.points_list[l-1]=self.end
            if(self.shape.shape_mode=='srect'):
                if self.shape.count == 1 or self.shape.count==2:
                    l=len(self.shape.points_list)
                    if(l<self.shape.count+1):
                        self.shape.points_list.append(self.end)
                    else:
                        self.shape.points_list[l-1]=self.end
                if self.shape.count==3:
                    self.shape.points_list[2]=self.end 
        self.update() #更新显示

    def mouseReleaseEvent(self, mouseEvent):
        self.end =  mouseEvent.pos()
        if(Qt.LeftButton==mouseEvent.button()):
            self.isPressed==False
            if(self.shape!=None):
                if(self.shape.shape_mode=='srect' or self.shape.shape_mode=='poly'):
                    if(self.shape.error==True):
                        self.shape=None 
                        self.__IsEmpty = False
                        return 
                self.shape_list.append(self.shape)
                self.shapeToBody(self.shape)
                self.shape=None
        self.__IsEmpty = False #画板不再为空
        
