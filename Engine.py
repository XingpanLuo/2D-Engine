from tkinter.messagebox import NO
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from numpy import *
from Collision import *
from Motion import *
import numpy as np
import math
"""
#  参考、引用说明：
# 
#  SAT分离轴算法参考:https://github.com/phenomLi/Blog/issues/23 
# 
# 
# 
# 
# 
# 
"""
def legal(a):
    temp=a/np.linalg.norm(a)
    return np.array([temp[1],-temp[0]])

def cross(w,r):
    a=w*r
    a=np.array([-a[1],a[0]])
    return a 
class Body():#刚体类
    def __init__(self) -> None:
        self.points_list=[] #刚体的顶点
        self.coll_points_list=[]
        self.coll_axes_list=[]
        self.axes_list=[] #各条边的法向量集合
        self.aabb=[]
        self.tree_id=0
        self.id=0   #全局id

        self.center=QPointF(0,0)    #圆的中心，之后可以作为质心
        self.radius=0   #圆的半径
        self.end=QPointF(0,0) 

        self.a=np.array([0.0,0.0])  #加速度
        self.v=np.array([0.0,0.0])  #速度

        self.g=np.array([0,0.98])  #重力加速度
        self.dt=np.array([0.1,0.1]) #模拟时间间隔

        self.position=np.array([0,0])   #位置
        self.rotation=0   #旋转角度
        #self.velocity=np.array([0,0])   #速度
        self.angular_velocity=0  #角速度
        self.mass=0
        self.invert_mass=0  #质量倒数
        self.inertia=0
        self.invert_inertia=0   #转动惯量倒数
        self.friction=0.5   #摩擦系数
        self.restitution=0.2    #恢复系数
        self.elasticity_factor=0.05 #弹性系数
        self.accumulated_normal_impulse=0   #累加法向冲量
        self.accumulated_tangent_impulse=0  #累加切向冲量

    def cal_parameter(self):
        self.cal_pos()
        self.cal_invert_mass()
        self.cal_invert_inertia()

    def cal_pos(self):
        self.position=pta(self.center)

    def cal_invert_mass(self):
        if self.invert_mass!=0:
            return
        if self.mode=='line':
            self.mass=infty
            self.invert_mass=0
            return 
        if self.mode=='circ':
            mass=math.pi*self.radius*self.radius
            self.mass=mass
            mass=1/mass
            self.invert_mass=mass
            return 
        mass=0
        l=len(self.points_list)
        for i in range(0,l-1):
            p=self.points_list[i]
            q=self.points_list[i+1]
            mass+=p.x()*q.y()
        mass+=self.points_list[l-1].x()*self.points_list[0].y()
        for i in range(1,l):
            p=self.points_list[i]
            q=self.points_list[i-1]
            mass-=p.x()*q.y()
        mass-=self.points_list[0].x()*self.points_list[l-1].y()
        mass/=2
        if mass<0:
            mass=-mass
        self.mass=mass
        self.invert_mass=1.0/mass
        return 

    def cal_invert_inertia(self):
        if self.invert_inertia!=0:
            return
        if self.mode=='line':
            self.inertia=infty
            self.invert_inertia=0
            return 
        if self.mode=='circ':
            inertia=0.5*self.mass*self.radius*self.radius
            self.inertia=inertia
            self.invert_inertia=1/inertia
            return 
        h=distance(self.points_list[0],self.points_list[1])
        w=distance(self.points_list[1],self.points_list[2])
        inertia=1/12*self.mass*(h*h+w*w)
        self.inertia=inertia
        self.invert_inertia=1/inertia
        return 

    def apply_impulse(self,impulse_n,r):
        if self.mode=='line':
            self.v=0
            self.angular_velocity=0
            return 
        self.v=self.v+impulse_n*self.invert_mass
        # if(np.linalg.norm(self.v)<0.00001):
        #     self.v=np.array([0,0])
        self.angular_velocity+=np.cross(r,impulse_n)*self.invert_inertia
        # if(abs(self.angular_velocity)<0.00001):
        #     self.angular_velocity=0
        if self.mode=='poly' or self.mode=='rect' or self.mode=='srect':
            for j in range(0,len(self.points_list)):
                p=self.points_list[j]
                array=pta(p)
                ap=array-self.position
                vp=self.v+cross(self.angular_velocity,ap-r)
                array=array+vp*self.dt
                p=atp(array)
                self.points_list[j]=p
        elif self.mode=='circ':
            array=pta(self.center)
            array=array+self.v*self.dt
            self.center=atp(array)
            array=pta(self.end)
            array=array+self.v*self.dt
            self.end=atp(array)


class Engine():
    def __init__(self) -> None:
        self.body_list=[]
        self.sat=SAT()
        self.motion=Motion()
        self.zero=np.array([0,0])

    def run(self):
        self.get_body_center()
        self.sat.sat_all(self.body_list)  #对所有刚体对象进行碰撞检测
        self.sat.get_coll_groups()
        for group in self.sat.coll_groups_list:
            self.motion.coll_motion(self.body_list[group.body1_id],self.body_list[group.body2_id],
            group.body1_points_and_axes,group.body2_points_and_axes)
        self.gravity()  #所有刚体受到重力，发生运动


    def get_body_center(self):
        for body in self.body_list:
            sum_x=0
            sum_y=0
            n=0
            if body.mode!='circ':
                for p in body.points_list:
                    sum_x=sum_x+p.x()
                    sum_y=sum_y+p.y()
                    n=n+1
                body.center=QPointF(sum_x/n,sum_y/n)

    def gravity(self):
        for i in self.body_list:
            if i.mode!='line':
                i.a=i.g 
                i.v=i.v+i.g*i.dt
                i.v=0.99*i.v
                i.angular_velocity=0.95*i.angular_velocity
            if i.mode=='poly' or i.mode=='rect' or i.mode=='srect':
                for j in range(0,len(i.points_list)):
                    p=i.points_list[j]
                    array=self.pta(p)
                    ap=array-i.position
                    vp=i.v+cross(i.angular_velocity,ap)
                    array=array+vp*i.dt
                    p=self.atp(array)
                    i.points_list[j]=p
            elif i.mode=='circ':
                array=self.pta(i.center)
                array=array+i.v*i.dt
                i.center=self.atp(array)
                array=self.pta(i.end)
                array=array+i.v*i.dt
                i.end=self.atp(array)
            else:
                i.v=np.array([0,0])
                i.angular_velocity=0

    def pta(self,p):    # QPointF => np.array
        t=[p.x(),p.y()]
        a=np.array(t)
        return a 
    
    def atp(self,a):    #np.array => QPointF
        l=a.tolist()
        t=QPointF(l[0],l[1])
        return t

    





