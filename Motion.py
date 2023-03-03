
import numpy as np
import math 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
def pta(p):
    return np.array([p.x(),p.y()])

def atp(a):    #np.array => QPointF
    l=a.tolist()
    t=QPointF(l[0],l[1])
    return t
def distance(p,q):
    return math.sqrt((p.x()-q.x())*(p.x()-q.x())+(p.y()-q.y())*(p.y()-q.y()))

def cross(w,r):
    a=w*r
    a=np.array([-a[1],a[0]])
    return a 

def clamp(add_t,min_t,max_t):
    if add_t<min_t:
        return min_t
    elif add_t>max_t:
        return max_t
    else:
        return add_t

class Motion(object):
    def __init__(self) -> None:
        self.rigid_list=[]

    def cal_parameter(self,body):
        self.cal_pos(body)
        self.cal_invert_mass(body)
        self.cal_invert_inertia(body)

    def cal_pos(self,body):
        body.position=pta(body.center)

    def cal_invert_mass(self,body):
        if body.invert_mass!=0:
            return
        if body.mode=='circ':
            mass=math.pi*body.radius*body.radius
            body.mass=mass
            mass=1/mass
            body.invert_mass=mass
            return 
        mass=0
        l=len(body.points_list)
        for i in range(0,l-1):
            p=body.points_list[i]
            q=body.points_list[i+1]
            mass+=p.x()*q.y()
        mass+=body.points_list[l-1].x()*body.points_list[0].y()
        for i in range(1,l):
            p=body.points_list[i]
            q=body.points_list[i-1]
            mass-=p.x()*q.y()
        mass-=body.points_list[0].x()*body.points_list[l-1].y()
        mass*=2
        body.mass=abs(mass)
        body.invert_mass=abs(1.0/mass)
        return 

    def cal_invert_inertia(self,body):
        if body.invert_inertia!=0:
            return
        if body.mode=='circ':
            inertia=0.5*body.mass*body.radius*body.radius
            body.inerita=inertia
            body.invert_inertia=1/inertia
            return 
        h=distance(body.points_list[0],body.points_list[1])
        w=distance(body.points_list[1],body.points_list[2])
        inertia=1/12*body.mass*(h*h+w*w)
        body.inertia=inertia
        body.invert_inertia=1/inertia
        return 


    def cal_new_state(self,body1,body2,coll_point,coll_axes):
        #计算碰撞冲量
        normal=pta(coll_axes)
        hight=np.linalg.norm(normal)
        pa=pta(coll_point)
        pb=pa+normal
        normal=normal/np.linalg.norm(normal)     #碰撞法线
        ra=pa-body1.position
        rb=pb-body2.position
        # if np.dot(normal,body1.v)>0:
        #     return np.array([0,0]),ra,rb
        im_a=body1.invert_mass
        im_b=body2.invert_mass
        ii_a=body1.invert_inertia
        ii_b=body2.invert_inertia
        rn_a=np.cross(ra,normal)
        rn_b=np.cross(rb,normal) 
        k_normal=im_a+ii_a*rn_a*rn_a+im_b+ii_b*rn_b*rn_b
        if abs(k_normal)<1e-15:
            effective_mass=0
        else:
            effective_mass=1.0/k_normal
        angular_va=body1.angular_velocity
        angular_vb=body2.angular_velocity
        wa=cross(angular_va,ra)
        wb=cross(angular_vb,rb)
        va=body1.v+wa
        vb=body2.v+wb 
        dv=va-vb
        jv=np.dot(dv,normal)
        bias=body1.elasticity_factor*max(0,hight-0.01)/body1.dt[0]
        jvb=-jv+bias 
        lambda_n=effective_mass*jvb
        old_impulse=body1.accumulated_normal_impulse
        body1.accumulated_normal_impulse=max(old_impulse+lambda_n,0)
        lambda_n=body1.accumulated_normal_impulse-old_impulse
        impulse_n=lambda_n*normal

        #计算摩擦冲量
        tangent=np.array([normal[1],-normal[0]])    #碰撞法线的切线
        if np.dot(dv,tangent)>0:
            tangent=-tangent
        rt_a=np.cross(ra,tangent)
        rt_b=np.cross(rb,tangent)
        k_tangent=im_a+ii_a*rt_a*rt_a+\
                im_b+ii_b*rt_b*rt_b
        if abs(k_tangent)<1e-15:
            effective_mass_tangent=0
        else:
            effective_mass_tangent=1.0/k_tangent
        jv=np.dot(dv,tangent)
        lambda_t=effective_mass_tangent*(-jv)
        max_t=abs(body2.friction*body1.accumulated_normal_impulse)
        old_impulse=body1.accumulated_tangent_impulse
        body1.accumulated_tangent_impulse=clamp(old_impulse+lambda_t,-max_t,max_t)
        lambda_t=body1.accumulated_tangent_impulse-old_impulse
        impulse_t=lambda_t*tangent
        return impulse_n,impulse_t,ra,rb 

    def coll_motion(self,body1,body2,body1_coll_points,body2_coll_points):
        body1.cal_parameter()
        body2.cal_parameter()
        for i in body1_coll_points:
            imp=self.cal_new_state(body1,body2,i[0],i[1])
            body1.apply_impulse(imp[0],imp[2])
            body2.apply_impulse(-imp[0],imp[3])
            body1.apply_impulse(imp[1],imp[2])
            body2.apply_impulse(-imp[1],imp[3])
        for i in body2_coll_points:
            imp=self.cal_new_state(body2,body1,i[0],i[1])
            body2.apply_impulse(imp[0],imp[2])
            body1.apply_impulse(-imp[0],imp[3])
            body2.apply_impulse(imp[1],imp[2])
            body1.apply_impulse(-imp[1],imp[3])