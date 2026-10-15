from __future__ import annotations
from PySide6.QtCore import QAbstractItemModel,QModelIndex,Qt
class Node:
    __slots__=('name','parent','children','record')
    def __init__(self,name='',parent=None,record=None):self.name=name;self.parent=parent;self.children=[];self.record=record
class FileTreeModel(QAbstractItemModel):
    def __init__(self,parent=None):super().__init__(parent);self.root=Node();self.by_path={}
    def clear(self):self.beginResetModel();self.root=Node();self.by_path={};self.endResetModel()
    def add_records(self,records):
        self.beginResetModel()
        for r in records:
            cur=self.root; acc=[]
            for part in r.relative_path.split('/'):
                acc.append(part); found=next((x for x in cur.children if x.name==part),None)
                if not found: found=Node(part,cur);cur.children.append(found)
                cur=found
            cur.record=r;self.by_path[r.relative_path]=cur
        self.endResetModel()
    def index(self,row,col,parent=QModelIndex()):
        n=parent.internalPointer() if parent.isValid() else self.root
        if 0<=row<len(n.children):return self.createIndex(row,col,n.children[row])
        return QModelIndex()
    def parent(self,index):
        if not index.isValid():return QModelIndex()
        p=index.internalPointer().parent
        if not p or p is self.root:return QModelIndex()
        return self.createIndex(p.parent.children.index(p),0,p)
    def rowCount(self,parent=QModelIndex()):return len((parent.internalPointer() if parent.isValid() else self.root).children)
    def columnCount(self,parent=QModelIndex()):return 2
    def data(self,index,role=Qt.DisplayRole):
        if not index.isValid():return None
        n=index.internalPointer()
        if role==Qt.DisplayRole:
            if index.column()==0:return n.name
            if n.record:return n.record.status.value.replace('_',' ').title()
        if role==Qt.UserRole:return n.record
        return None
    def headerData(self,s,o,role=Qt.DisplayRole):return ['Path','Status'][s] if role==Qt.DisplayRole and o==Qt.Horizontal and s<2 else None
