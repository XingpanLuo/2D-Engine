from typing import Set
import numpy as np
import math 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
import queue 
from Ftree import *
def pta(p):    # QPointF => np.array
    t=[p.y(),p.x()]
    a=np.array(t)
    return a 

def atp(a):    #np.array => QPointF
    l=a.tolist()
    t=QPointF(l[1],l[0])
    return t

def is_over_laps(pro1,pro2):
    #直线L1与直线L2是否有重叠：
    #L1的右端点小于L2的左端点 或 L1的左端点大于L2的右端点 ，此时，两直线不重叠
    if pro1[0]>=pro2[1] or pro1[1]<=pro2[0]:
        return 0
    else:
        min1=max(pro1[0],pro2[0])
        min2=min(pro1[1],pro2[1])
        return min2-min1

class AABB_Point():
    def __init__(self,x,y,is_start,id) -> None:
        self.x=x
        self.y=y
        self.is_start=is_start
        self.id=id

class AABB():
    def __init__(self) -> None:
        pass

    def get_aabb(self,body_list):
        aabb_list=[]
        for i in range(0,len(body_list)):
            aabb=[0,0,0,0]
            b=body_list[i]
            if b.mode=='circ':
                p=b.center
                aabb[0]=p.x()-b.radius
                aabb[1]=p.x()+b.radius
                aabb[2]=p.y()-b.radius
                aabb[3]=p.y()+b.radius
            else:
                list_a=[p.x() for p in b.points_list]
                list_b=[p.y() for p in b.points_list]
                aabb[0]=min(list_a)
                aabb[1]=max(list_a)
                aabb[2]=min(list_b)
                aabb[3]=max(list_b)
            body_list[i].aabb=aabb
            aabb_list.append(AABB_Point(aabb[0],aabb[2],True,i))
            aabb_list.append(AABB_Point(aabb[1],aabb[3],False,i))
        # for i in aabb_list:
        #     print("test:",i.x,i.is_start,i.id)
        return aabb_list
    
    def detection(self,body1,body2):
        pro1=body1.aabb[0:2]
        pro2=body2.aabb[0:2]
        pro3=body1.aabb[2:4]
        pro4=body2.aabb[2:4]
        # print(pro1,pro2,pro3,pro4)
        if is_over_laps(pro1,pro2)==0 or is_over_laps(pro3,pro4)==0:
            return False
        else:
            return True 
class CollGroup():
    def __init__(self,body1_id=0,body2_id=0,body1_points=[],body2_points=[]) -> None:
        self.body1_id=body1_id
        self.body2_id=body2_id
        self.body1_points_and_axes=body1_points
        self.body2_points_and_axes=body2_points

class SAT():
    def __init__(self) -> None:
        self.aabb=AABB()
        self.body_list=[]
        self.tree=Tree()
        self.board=None
        self.aabb_list=[]

    def distance(self,p1,p2):   #QPoint,两点间距离
        if(isinstance(p1,QPointF) or isinstance(p1,QPoint)):
            x1=p1.x()
            x2=p2.x()
            y1=p1.y()
            y2=p2.y()
            return math.sqrt((x1-x2)**2+(y1-y2)**2)
        else:
            return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

    def get_poly_axes(self,body):   #计算多边形的分离轴（边的法向量集合
        axes_list=[]
        list=body.points_list
        for i in range(0,len(list)):
            #遍历每条边
            p=QPointF(list[i].x()-list[i-1].x(),list[i].y()-list[i-1].y())
            a=pta(p)
            #每条边的法向量
            n=np.array([-a[1],a[0]])
            n=n/np.linalg.norm(n)
            axes_list.append(n)
        return axes_list 

    def get_circ_axes(self,circ_body,poly_body):
        #圆的分离轴，距离圆心最近的点与圆心的连线
        index=0
        center=circ_body.center
        vexs=poly_body.points_list
        min_len=self.distance(vexs[0],center)
        for i in range(1,len(vexs)):
            l=self.distance(vexs[i],center)
            if(l<min_len):
                min_len=l
                index=i
        p=QPointF(vexs[index].x()-center.x(),vexs[index].y()-center.y())
        a=pta(p)
        a=a/np.linalg.norm(a)
        list=[a]
        return list 

    def get_axes(self,body1,body2)->list:
        #任意两个刚体的分离轴集合，body是圆和多边形，分别用不同的方法得到分离轴，合并一下就行
        axes_list1=[]
        axes_list2=[]
        if(body1.mode=='circ'):
            axes_list1=self.get_circ_axes(body1,body2)
        else:
            axes_list1=self.get_poly_axes(body1)
        if(body2.mode=='circ'):
            axes_list2=self.get_circ_axes(body2,body1)
        else:
            axes_list2=self.get_poly_axes(body2)
        axes_list=axes_list1+axes_list2
        # print("axes_list1:",axes_list1,"axes_list2:",axes_list2)
        return axes_list

    def project(self,body,axis)->list:
        #刚体body的所有点在分离轴axis上的投影区间
        #投影计算方法：
        """向量a在向量b上的投影
        vec_a*vec_b=|vec_a|*|vec_b|*cos
        投影len=|vec_a|*cos=(vec_a*vec_b)/|vec_b|
        """
        #norm=np.linalg.norm(axis)   #axis的模
        if(body.mode!='circ'):
            list=[]
            #每个顶点的分离轴投影的最小值与最大值，构成投影区间
            for p in body.points_list:
                a=pta(p)
                list.append(np.dot(a,axis))
            range=[min(list),max(list)]
        else:
            #圆的分离轴投影：圆心的分离轴投影加减半径
            center=pta(body.center)
            radius=body.radius
            len=np.dot(axis,center)
            range=[len-radius,len+radius]
        return range
        
    def poly_sat(self,body1,body2)->bool:
        #多边形与多边形，多边形与圆，做SAT碰撞检测
        #得到分离轴集合
        axes=self.get_axes(body1,body2)
        #对每个分离轴，分别计算两个body的投影区间
        flag=True 
        min_pro=infty 
        min_axes=[]
        for i in range(0,len(axes)):
            pro1=self.project(body1,axes[i])
            pro2=self.project(body2,axes[i])
            #检测投影区间是否有重叠，只要有一次不重叠，说明无碰撞
            l=is_over_laps(pro1,pro2)
            if(l<0.0001):
                flag=False
                return (flag,min_pro,min_axes)
            else:
                if l<min_pro:
                    min_pro=l
                    #min_axes=np.array(axes[i][1],axes[i][0])
                    min_axes=np.array(axes[i])
        if min_pro>0.1:
            flag=True
        #print(min_axes)
        return (flag,min_pro,min_axes)


    def circ_sat(self,body1,body2):
        #对两个圆做碰撞检测
        #圆心距大于半径和，说明无碰撞，否则发生碰撞
        distance=self.distance(body1.center,body2.center)
        sum_radius=body1.radius+body2.radius
        c1=pta(body1.center)
        c2=pta(body2.center)
        a=np.array([c1[0]-c2[0],c1[1]-c2[1]])
        n=np.array([-a[1],a[0]])
        min_pro=sum_radius-distance
        if(distance>sum_radius):
            return (False,min_pro,n)
        else:
            return (True,min_pro,n)
    
    def sat_detection(self,body1,body2):
        if(body1.mode=='circ' and body2.mode=='circ'):
            return self.circ_sat(body1,body2)
        else:
            return self.poly_sat(body1,body2)

    def stillness(self,body):
        #body.a=np.array([0,0])
        body.v=np.array([0,0])
        body.g=np.array([0,0])
        body.angular_velocity=0

    def move(self,body,s,n):
        i=body 
        if i.mode=='poly' or i.mode=='rect' or i.mode=='srect':
                for j in range(0,len(i.points_list)):
                    p=i.points_list[j]
                    array=pta(p)
                    array=array+s*n
                    p=atp(array)
                    i.points_list[j]=QPointF(p)
        elif i.mode=='circ':
                array=pta(i.center)
                array=array+s*n
                i.center=atp(array)
                array=pta(i.end)
                array=array+s*n
                i.end=atp(array)

    def detection(self,body1_id,body2_id):
        body1=self.body_list[body1_id]
        body2=self.body_list[body2_id]
        #if self.tree.detection(body1.aabb,body2.aabb):
            #aabb 粗检测
        if(self.aabb.detection(body1,body2)):
            #SAT 细检测
            dete=self.sat_detection(body1,body2)    #返回一个元组(bool,float,array)
            if(dete[0]==True):  
                coll=(body1.id,body2.id,dete[1],dete[2])  #body1,body2发生碰撞，碰撞深度为coll[2],碰撞法线为coll[3]
                # self.stillness(body1)
                # self.stillness(body2)
                self.collision_list.append(coll)

    #sweep and prune
    #https://github.com/phenomLi/Blog/issues/22
    def sweep(self):
        L=[]
        may_list=[]
        for i in self.aabb_list:
            if i.is_start:
                L.append(i)
                for j in range(0,len(L)-1): 
                    body1_id=min(i.id,L[j].id)
                    body2_id=max(i.id,L[j].id)
                    #if body1_id!=0 and body2_id!=0:
                    may_list.append([body1_id,body2_id])
            else:
                for j in range(0,len(L)):
                    if L[j].id==i.id:
                        del L[j]
                        break 
        return may_list 

    def sat_all(self,body_list):
        self.body_list=body_list
        self.collision_list=[]
        #self.tree.get_all_tree_id(self.body_list)
        self.aabb_list=self.aabb.get_aabb(self.body_list)
        self.aabb_list.sort(key=lambda p : p.x)
        sweep_collision_list=self.sweep()
        for i in sweep_collision_list:
            self.detection(i[0],i[1])

    
    def get_polys_coll_points(self,coll):   #poly与poly碰撞,得到两个body的碰撞点和碰撞法线
        body1_coll_points=[]
        body2_coll_points=[]
        body1=self.body_list[coll[0]]
        body2=self.body_list[coll[1]]
        num=0
        coll_axes=atp(coll[2]*coll[3])
        cn=body1.center-body2.center
        if coll_axes.x()*cn.x()+coll_axes.y()*cn.y()<0:
            coll_axes*=-1 
        axes=pta(coll_axes)
        temp=[]
        for p in body1.points_list:
            a=pta(p)
            mul_res=np.dot(a,axes)
            temp.append([p,mul_res])
        temp.sort(key=lambda x:x[1])
        p=temp[0][0]
        if self.if_point_in_polygon(p,body2.points_list):
            body1.coll_points_list.append(p)
            body1.coll_axes_list.append(coll_axes)
            body1_coll_points.append([p,coll_axes])
            num=num+1
        p=temp[1][0]
        if  self.if_point_in_polygon(p,body2.points_list):
            body1.coll_points_list.append(p)
            if num==1:
                q=temp[0][0]
                n_axes=axes/np.linalg.norm(axes)
                pq=pta(p)-pta(q)
                l=abs(np.dot(pq,n_axes))
                axes=axes-l*n_axes
                coll_axes=atp(axes)
            body1.coll_axes_list.append(coll_axes)
            body1_coll_points.append([p,coll_axes])
            num=num+1
        if num==2:
            group=CollGroup(coll[0],coll[1],body1_coll_points,body2_coll_points)
            return group 
        coll_axes=atp(coll[2]*coll[3])
        cn=body2.center-body1.center
        if coll_axes.x()*cn.x()+coll_axes.y()*cn.y()<0:
            coll_axes*=-1
        axes=pta(coll_axes)
        temp.clear()
        for p in body2.points_list:
            a=pta(p)
            mul_res=np.dot(a,axes)
            temp.append([p,mul_res])
        temp.sort(key=lambda x:x[1])
        p=temp[0][0]
        if self.if_point_in_polygon(p,body1.points_list):
            body2.coll_points_list.append(p)
            body2.coll_axes_list.append(coll_axes)
            body2_coll_points.append([p,coll_axes])
            num=num+1
        if num==2:
            group=CollGroup(coll[0],coll[1],body1_coll_points,body2_coll_points)
            return group 
        p=temp[1][0]
        if self.if_point_in_polygon(p,body1.points_list):
            body2.coll_points_list.append(p)
            if num==1:
                q=temp[0][0]
                n_axes=axes/np.linalg.norm(axes)
                pq=pta(p)-pta(q)
                l=abs(np.dot(pq,n_axes))
                axes=axes-l*n_axes
                coll_axes=atp(axes)
            body2.coll_axes_list.append(coll_axes)
            body2_coll_points.append([p,coll_axes])
            num=num+1
        
        group=CollGroup(coll[0],coll[1],body1_coll_points,body2_coll_points)
        return group
        
    def get_circ_circ_coll_points(self,coll):
        body1_coll_points=[]
        body2_coll_points=[]
        #print(coll[3])
        if(self.body_list[coll[0]].mode=='circ' and self.body_list[coll[1]].mode=='circ'):
            #圆与圆碰撞
            body1=self.body_list[coll[0]]
            body2=self.body_list[coll[1]]
            temp=body1.center-body2.center
            dis=self.distance(body1.center,body2.center)
            cn=QPointF(temp.x()/dis,temp.y()/dis)
            delta_dis=body1.radius+body2.radius-dis
            coll_axes=QPointF(cn.x()*delta_dis,cn.y()*delta_dis)
            p=QPointF(body2.center.x()+cn.x()*body2.radius,body2.center.y()+cn.y()*body2.radius)
            body2.coll_points_list.append(p)
            body2.coll_axes_list.append(-coll_axes)
            body2_coll_points.append([p,-coll_axes])

            cn=-cn
            coll_axes=-coll_axes
            p=QPointF(body1.center.x()+cn.x()*body1.radius,body1.center.y()+cn.y()*body1.radius)
            body1.coll_points_list.append(p)
            body1.coll_axes_list.append(-coll_axes)
            body1_coll_points.append([p,-coll_axes])
            group=CollGroup(coll[0],coll[1],body1_coll_points,body2_coll_points)
            #print(coll[0],coll[1],body1_coll_points,body2_coll_points)
            return group

    def get_poly_circ_coll_points(self,coll):
        body1_coll_points=[]
        body2_coll_points=[]
        body1=self.body_list[coll[0]]
        body2=self.body_list[coll[1]]
        #先求body2的碰撞点及碰撞法线
        coll_axes=atp(coll[2]*coll[3])
        norm_axes=atp(coll[3])
        cn=body2.center-body1.center
        if coll_axes.x()*cn.x()+coll_axes.y()*cn.y()<0:
            coll_axes*=-1 
            norm_axes=-norm_axes
            
        axes=pta(cn)
        temp=[]
        for p in body2.points_list:
            a=pta(p)
            mul_res=np.dot(a,axes)
            temp.append([p,mul_res])
        temp.sort(key=lambda x:x[1])
        p=temp[0][0]
        flag=False
        if self.distance(p,body1.center)<body1.radius:
            body2.coll_points_list.append(p)
            body2.coll_axes_list.append(coll_axes)
            body2_coll_points.append([p,coll_axes])
            flag=True
        #求body1的碰撞点和碰撞法线
        if not flag:
            p=body1.center+norm_axes*body1.radius
        else:
                p=p+coll_axes
        body1.coll_points_list.append(p)
        body1.coll_axes_list.append(-coll_axes)
        body1_coll_points.append([p,-coll_axes])
        group=CollGroup(coll[0],coll[1],body1_coll_points,body2_coll_points)
        return group


    def get_coll_groups(self):
        for body in self.body_list:
            body.coll_points_list.clear()
            body.coll_axes_list.clear()
        self.coll_groups_list=[]
        for coll in self.collision_list:
            if(self.body_list[coll[0]].mode!='circ' and self.body_list[coll[1]].mode!='circ'):
                group=self.get_polys_coll_points(coll)
                self.coll_groups_list.append(group)
            elif(self.body_list[coll[0]].mode=='circ' and self.body_list[coll[1]].mode=='circ'):
                group=self.get_circ_circ_coll_points(coll)
                self.coll_groups_list.append(group)
            elif(self.body_list[coll[0]].mode=='circ'):
                group=self.get_poly_circ_coll_points(coll)
                self.coll_groups_list.append(group)
            else:
                n_coll=(coll[1],coll[0],coll[2],coll[3])
                group=self.get_poly_circ_coll_points(n_coll)
                self.coll_groups_list.append(group)
   
    def if_point_in_polygon(self,p,points_list):
        x=p.x()
        y=p.y()
        count=len(points_list)
        isInside=False
        precision=0.01
        i=0
        j=count-1
        while i<count:
            x1=points_list[i].x()
            y1=points_list[i].y()
            x2=points_list[j].x()
            y2=points_list[j].y()
            if((x1==x and y1==y) or (x2==x and y2==y)):
                return True
            if(y==y1 and y==y2):
                if x>=min(x1,x2) and x<=max(x1,x2):
                    return True
            if((y>=y1 and y<y2) or (y<y1 and y>=y2)):
                k=(x2-x1)/(y2-y1)
                _x=x1+k*(y-y1)
                if abs(_x-x)<precision:
                    return True
                if _x>x:
                    isInside=not isInside
            j=i
            i=i+1
        return isInside
