from __future__ import annotations
import sys, threading, shutil, time
from pathlib import Path
from PySide6.QtCore import Qt,Signal,QObject,QSettings
from PySide6.QtWidgets import *
from storage.database import Database
from storage.profiles import ProfileStore,Profile
from core.scanner import scan
from core.diff_engine import unified
from core.sync_engine import atomic_copy
from widgets.file_tree_model import FileTreeModel

class Bridge(QObject):
    batch=Signal(object); progress=Signal(int,int); done=Signal(); error=Signal(str); diff=Signal(str)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('ProjectSync');self.resize(1400,850);self.bridge=Bridge();self.cancel=threading.Event();self.pause=threading.Event();self.pause.set();self.records={};self.store=ProfileStore();self.profiles=self.store.load_all();self.db=Database(self.store.dir/'cache.db');self._ui();self._connect();self.load_profile('Default')
    def _ui(self):
        w=QWidget();self.setCentralWidget(w);v=QVBoxLayout(w);g=QGridLayout();v.addLayout(g)
        self.local=QLineEdit();self.up=QLineEdit();self.profile=QComboBox();self.profile.addItems(self.profiles);self.newup=QCheckBox('Show new upstream files')
        g.addWidget(QLabel('Local:'),0,0);g.addWidget(self.local,0,1);b=QPushButton('Browse');b.clicked.connect(lambda:self.browse(self.local));g.addWidget(b,0,2)
        g.addWidget(QLabel('Upstream:'),1,0);g.addWidget(self.up,1,1);b2=QPushButton('Browse');b2.clicked.connect(lambda:self.browse(self.up));g.addWidget(b2,1,2)
        g.addWidget(QLabel('Profile:'),2,0);g.addWidget(self.profile,2,1);save=QPushButton('Save Profile');save.clicked.connect(self.save_profile);g.addWidget(save,2,2);g.addWidget(self.newup,3,1)
        h=QHBoxLayout();v.addLayout(h);self.scanb=QPushButton('Scan');self.pauseb=QPushButton('Pause');self.cancelb=QPushButton('Cancel');[h.addWidget(x) for x in (self.scanb,self.pauseb,self.cancelb)];h.addStretch()
        self.model=FileTreeModel();self.tree=QTreeView();self.tree.setModel(self.model);self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection);self.diff=QPlainTextEdit();self.diff.setReadOnly(True);self.diff.setLineWrapMode(QPlainTextEdit.NoWrap)
        sp=QSplitter();sp.addWidget(self.tree);sp.addWidget(self.diff);sp.setSizes([500,900]);v.addWidget(sp,1);self.status=QLabel('Ready');v.addWidget(self.status);self.splitter=sp
    def _connect(self):
        self.scanb.clicked.connect(self.start_scan);self.pauseb.clicked.connect(self.toggle_pause);self.cancelb.clicked.connect(self.cancel_scan);self.profile.currentTextChanged.connect(self.load_profile);self.tree.selectionModel().currentChanged.connect(self.selected);self.bridge.batch.connect(self.add_batch);self.bridge.progress.connect(lambda a,b:self.status.setText(f'Scanning… {a:,}/{b:,}'));self.bridge.done.connect(lambda:self.status.setText(f'Done — {len(self.records):,} tracked files'));self.bridge.error.connect(lambda x:QMessageBox.critical(self,'Error',x));self.bridge.diff.connect(self.diff.setPlainText)
    def browse(self,e):
        p=QFileDialog.getExistingDirectory(self,'Select directory',e.text()); e.setText(p) if p else None
    def load_profile(self,name):
        p=self.profiles.get(name);
        if p:self.local.setText(p.local_root);self.up.setText(p.upstream_root);self.newup.setChecked(p.show_new_upstream_files)
    def save_profile(self):
        n=self.profile.currentText() or 'Default';self.profiles[n]=Profile(n,self.local.text(),self.up.text(),[],['.git/**','build/**','out/**'],self.newup.isChecked());self.store.save_all(self.profiles);self.status.setText('Profile saved')
    def start_scan(self):
        l,u=Path(self.local.text()),Path(self.up.text())
        if not l.is_dir() or not u.is_dir():QMessageBox.warning(self,'Paths','Select valid Local and Upstream directories.');return
        self.cancel.clear();self.pause.set();self.records.clear();self.model.clear();p=self.profiles.get(self.profile.currentText(),Profile());p.local_root=str(l);p.upstream_root=str(u);p.show_new_upstream_files=self.newup.isChecked()
        def job():
            try:scan(l,u,p.include,p.exclude,p.show_new_upstream_files,self.db,self.cancel,self.pause,8,lambda b:self.bridge.batch.emit(b),lambda a,b:self.bridge.progress.emit(a,b))
            except Exception as e:self.bridge.error.emit(str(e))
            self.bridge.done.emit()
        threading.Thread(target=job,daemon=True).start()
    def add_batch(self,b):
        for r in b:self.records[r.relative_path]=r
        self.model.add_records(b)
    def toggle_pause(self):
        if self.pause.is_set():self.pause.clear();self.pauseb.setText('Resume');self.status.setText('Paused')
        else:self.pause.set();self.pauseb.setText('Pause')
    def cancel_scan(self):self.cancel.set();self.pause.set();self.status.setText('Cancelling…')
    def selected(self,idx,_):
        r=idx.data(Qt.UserRole) if idx.isValid() else None
        if not r:return
        l=Path(self.local.text())/r.relative_path;u=Path(self.up.text())/r.relative_path
        def job():
            try:self.bridge.diff.emit(unified(l,u,r.relative_path) if l.exists() and u.exists() else f'{r.status.value}: {r.relative_path}')
            except Exception as e:self.bridge.diff.emit(str(e))
        threading.Thread(target=job,daemon=True).start()
    def contextMenuEvent(self,e):pass

def run():
    app=QApplication(sys.argv);app.setOrganizationName('ProjectSync');app.setApplicationName('ProjectSync');w=MainWindow();w.show();return app.exec()
