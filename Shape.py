
import math
from PyQt5.Qt import *
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from abc import ABCMeta,abstractmethod
MODES=['line','poly','rect','ellipse','freehand']
"""
# 重要参考、引用说明：
# 绘制斜矩形Shape.SRect.calc_polygon()函数的算法参考：https://blog.csdn.net/this_is_id/article/details/123050230
# 
#
#
#
"""
class Shape:
    __metaclass__=ABCMeta
    def __init__(self) -> None:
        self.start=QPointF(0,0)
        self.end=QPointF(0,0)
        self.color=Qt.black
        self.width=1
        self.shape_mode='line'
        self.coll_points_list=[]
        self.coll_axes_list=[]
    
    @abstractmethod
    def draw(self,qp):
        pass
    def set_start(self,s):
        self.start=s

    def set_end(self,e):
        self.end=e 

    def set_line(self,line_color,line_width):
        self.color=line_color
        self.width=line_width

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def draw_coll_point(self,qp):
        #return 
        for i in range(len(self.coll_points_list)):
            p=self.coll_points_list[i]
            axes=self.coll_axes_list[i]
            qp.setPen(QPen(QColor(127,255,0), 10,Qt.SolidLine,Qt.RoundCap))
            qp.drawPoint(p)
            q=QPointF(p.x()+axes.x(),p.y()+axes.y())
            qp.setPen(QPen(QColor(127,255,0), 5,Qt.SolidLine,Qt.RoundCap))
            qp.drawLine(p,q)

class Rect(Shape):
    def __init__(self,board=None) -> None:
        super().__init__()
        self.shape_mode='rect'
        self.color=board.color
        self.width=board.width
        self.points_list=[]
    
    def draw(self,qp):
        qp.setPen(QPen(self.color,self.width))
        rect=QRectF(self.start.x(),self.start.y(),
            self.end.x()-self.start.x(),self.end.y()-self.start.y())
        if(len(self.points_list)==0):
            qp.drawRect(rect)
        elif(self.points_list[0].y()!=self.points_list[1].y()):
            qp.drawPolygon(QPolygonF(self.points_list))
        else:
            qp.drawRect(rect)
        self.draw_coll_point(qp)

class Line(Shape):
    def __init__(self,board=None) -> None:
        super().__init__()
        self.shape_mode='line'
        #self.board=board
        self.color=board.color
        self.width=board.width
        self.points_list=[QPointF(0,0),QPointF(0,0),QPointF(0,0),QPointF(0,0)]
    
    def draw(self,qp):
        qp.setPen(QPen(self.color,self.width))
        brush=QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.DiagCrossPattern)
        qp.setBrush(brush)
        if(self.start.x()!=self.end.x() or self.start.y()!=self.end.y()):
            self.calc_polygon(6)
            try:
                qp.drawPolygon(QPolygonF(self.points_list))
            except:
                print("error drawLine_drawRect")
            qp.setBrush(QBrush(Qt.NoBrush))
        self.draw_coll_point(qp)

    def calc_polygon(self,t=6):
        self.count=3
        point1=self.start
        point2=self.end
        self.points_list[0]=self.start
        self.points_list[1]=self.end
        x1 = point1.x()
        y1 = point1.y()
        x2 = point2.x()
        y2 = point2.y()
        try:
            k=(y1-y2)/(x1-x2)
        except:
            k=10
        if abs(y1-y2)<0.0001 or abs(k)<0.1:
            if x2-x1>0:
                t=-15.7
            else:
                t=15.7
            point2=QPointF(point2.x(),point1.y())
            point3=QPointF(point2.x(),point2.y()+t)
            point4=QPointF(point1.x(),point1.y()+t)
            self.points_list[1]=point2
            self.points_list[2]=point3
            self.points_list[3]=point4
            return 
        l=math.sqrt((x2-x1)**2+(y2-y1)**2)
        sin=(y2-y1)/l
        t/=sin
        t*=2.5
        cursor_point=QPointF(self.end.x(),self.end.y()+t)
        if abs(t)<0.01:
            cursor_point=QPointF(self.end.x(),self.end.y()+t)
        else:
            cursor_point=QPointF(self.end.x()+t,self.end.y())
        x3 = cursor_point.x()
        y3 = (x2 ** 2 - 2 * x1 * x2 + y2 ** 2 - 2 * y1 * y2 + y2 ** 2 + x2 ** 2 - 2 * x2 * x3 + 2 * x1 * x3) / (
                2 * y2 - 2 * y1)
        dx = x2 - x3
        dy = y2 - y3
        if abs(dx) < 0.00000001 and abs(dy) < 0.00000001:
            return
        u = (cursor_point.x() - x2) * (x2 - x3) + (cursor_point.y() - y2) * (y2 - y3)
        u = u / ((dx * dx) + (dy * dy))
        x3 = x2 + u * dx
        y3 = y2 + u * dy
        point3 = QPointF(x3, y3)
        self.points_list[2]=point3
        x4 = x1 + x3 - x2
        y4 = y1 + y3 - y2
        point4 = QPointF(x4, y4)
        self.points_list[3]=point4

class Poly(Shape):
    def __init__(self,board=None) -> None:
        super().__init__()
        self.shape_mode='poly'
        self.color=board.color
        self.width=board.width
        self.points_list=[]
        self.point_nums=0
        self.error=True 
    
    def draw(self,qp):
        qp.setPen(QPen(self.color,self.width))
        polygon = QPolygonF(self.points_list)
        qp.drawPolygon(polygon)
        if(len(self.points_list)>2):
            self.error=False
        self.draw_coll_point(qp)
        
    def addNum(self):
        self.point_nums=self.point_nums+1

class SRect(Shape):
    def __init__(self,board=None) -> None:
        super().__init__()
        #self.board=board
        self.shape_mode='srect'
        self.color=board.color
        self.width=board.width
        self.count=0
        self.points_list=[]
        self.line=None
        self.polygon=None
        self.error=True
        self.rect=False 
    
    def draw(self,qp):
        qp.setPen(QPen(self.color,self.width))
        l=len(self.points_list)
        if(self.rect and l==4):
            qp.drawPolygon(QPolygonF(self.points_list))
            self.draw_coll_point(qp)
            return
        if l==2:
            self.calc_line()
            qp.drawLine(self.line)
        elif l==3 or l==4:
            #print("test drawPolygon")
            try:
                self.calc_polygon()
            except:
                pass 
            #print("test ")
            l=len(self.points_list)
            #print("l:",l)
            if(l==4):
                qp.drawPolygon(self.polygon)
                self.error=False
            elif(l>=2 and l<4):
                #print("polygon's points < 4")
                qp.drawLine(self.line)
            else:
                pass 
        else:
            pass
        self.draw_coll_point(qp)

    def calc_line(self):
        point1=self.points_list[0]
        point2=self.points_list[1]
        self.line = QLineF(point1, point2)


    def calc_polygon(self):
        self.count=3
        point1=self.points_list[0]
        point2=self.points_list[1]
        cursor_point=self.points_list[2]
        x1 = point1.x()
        y1 = point1.y()
        x2 = point2.x()
        y2 = point2.y()
        x3 = cursor_point.x()
        y3 = (x2 ** 2 - 2 * x1 * x2 + y2 ** 2 - 2 * y1 * y2 + y2 ** 2 + x2 ** 2 - 2 * x2 * x3 + 2 * x1 * x3) / (
                2 * y2 - 2 * y1)
        dx = x2 - x3
        dy = y2 - y3
        if abs(dx) < 0.00000001 and abs(dy) < 0.00000001:
            return
        u = (cursor_point.x() - x2) * (x2 - x3) + (cursor_point.y() - y2) * (y2 - y3)
        u = u / ((dx * dx) + (dy * dy))
        x3 = x2 + u * dx
        y3 = y2 + u * dy
        point3 = QPointF(x3, y3)
        self.points_list[2]=point3
        x4 = x1 + x3 - x2
        y4 = y1 + y3 - y2
        point4 = QPointF(x4, y4)
        if len(self.points_list)==4:
            self.points_list[3]=point4
        else:
            self.points_list.append(point4)
        self.polygon = QPolygonF(self.points_list)

class Circ(Shape):
    def __init__(self,board=None) -> None:
        super().__init__()
        self.shape_mode='circ'
        self.color=board.color
        self.width=board.width
        self.radius=-1


    def draw(self,qp):
        self.radius=self.distance()
        qp.setPen(QPen(self.color,self.width))
        qp.drawEllipse(self.start,self.radius,self.radius)
        self.draw_coll_point(qp)

    def distance(self):
        return math.sqrt((self.end.x()-self.start.x())**2+(self.end.y()-self.start.y())**2)