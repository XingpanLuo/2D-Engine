from PyQt5.QtCore import *
from Engine import *
NUM_OF_NODE=85
MAX_WIDTH=1440
MAX_HEIGHT=1624
PER_WIDTH=MAX_WIDTH//8
PER_HEIGHT=MAX_HEIGHT//8
class Node():
    def __init__(self,list=[0,0,0,0],id=0) -> None:
        self.range=list
        self.id=id
        self.body_list=[]
        
class Tree():
    def __init__(self) -> None:
        self.nodes_list=[Node()]*NUM_OF_NODE
        for i in range(0,NUM_OF_NODE):
            node=Node([0,0,0,0],i)
            self.nodes_list[i]=node 
        self.valid_set=set()  #node_list中有效的id
        self.build()
        

    def child(self,i,k)->Node: #节点i的第k个节点,k=1,2,3,4
        if 4*i+k>NUM_OF_NODE-1:
            return None
        else:
            return self.nodes_list[int(4*i+k)]

    def parent(self,i):
        if i==0 or i>NUM_OF_NODE-1:
            return self.nodes_list[0] 
        k=(i-1)//4
        return self.nodes_list[k]

    def build(self):
        wl=1
        wr=1440
        hl=1
        hr=1624
        self.nodes_list[0].range=[wl,wr,hl,hr]
        for i in range(1,NUM_OF_NODE):
            parent=self.parent(i)
            [wl,wr,hl,hr]=parent.range
            k=(i-1)%4
            w=int((wr+wl)//2)
            h=int((hr+hl)//2)
            if k==0:
                self.nodes_list[i].range=[wl,w,hl,h]
            elif k==1:
                self.nodes_list[i].range=[w+1,wr,hl,h]
            elif k==2:
                self.nodes_list[i].range=[wl,w,h+1,hr]
            elif k==3:
                self.nodes_list[i].range=[w+1,wr,h+1,hr]
            self.nodes_list[i].id=i
    
    def if_in_rect(self,range,x,y): #点(x,y)是否在range表示的矩形中
        if x>=range[0] and x<=range[1]:
            if y>=range[2] and y<=range[3]:
                return True
        return False
     
    def get_xy_id(self,x,y):#点(x,y)在编号(id)为几的叶子节点中
        m=x//720
        n=y//814
        i=int(1+2*n+m)
        while(self.child(i,1)!=None):
            j=-1
            for k in range(1,5):
                if self.if_in_rect((self.child(i,k)).range,x,y)==True:
                    j=k
                    break 
            if j==-1:
                return j
            i=self.child(i,j).id 
        return i 
    
    def get_aabb_tree_id(self,aabb):
        x1=aabb[0]
        y1=aabb[2]
        x2=aabb[1]
        y2=aabb[2]
        x3=aabb[0]
        y3=aabb[3]
        x4=aabb[1]
        y4=aabb[3]
        id=self.get_xy_id(x1,y1)
        if id==-1:
            return 0
        while self.if_in_rect(self.nodes_list[id].range,x2,y2)==False and id!=0:
            id=self.parent(id).id
        while self.if_in_rect(self.nodes_list[id].range,x3,y3)==False and id!=0:
            id=self.parent(id).id
        while self.if_in_rect(self.nodes_list[id].range,x4,y4)==False and id!=0:
            id=self.parent(id).id
        return id 
    
    # def get_all_tree_id(self,body_list):
    #     body_list[0].tree_id=0
    #     for i in range(1,len(body_list)):
    #         aabb=body_list[i].aabb
    #         body_list[i].tree_id=self.get_aabb_tree_id(aabb)

    def detection(self,aabb1,aabb2):
        id1=self.get_aabb_tree_id(aabb1)
        id2=self.get_aabb_tree_id(aabb2)
        if id1==id2 or id1==0 or id2==0:
            return True
        max_id=max(id1,id2)
        min_id=min(id1,id2)
        if min_id>=1 and min_id<5:
            min_h=1
        elif min_id>=5 and min_id<21:
            min_h=2
        else:
            min_h=3
        if max_id>=1 and max_id<5:
            max_h=1
        elif max_id>=5 and max_id<21:
            max_h=2
        else:
            max_h=3
        if max_h==min_h:
            return False
        delta_h=max_h-min_h 
        for i in range(0,delta_h):
            min_id=self.parent(min_id).id 
        if min_id==max_id:
            return True
        else:
            return False
        
        
if __name__=="__main__":
    tree=Tree()
    i=tree.get_xy_id(1100,1324)
    print(i)






