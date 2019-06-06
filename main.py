import sys
from PySide2 import QtCore, QtGui
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHBoxLayout, QTextEdit, QHeaderView, QCheckBox, QWidgetItem
from PySide2.QtCore import Slot, Qt
from helper import process_document
import queue
from Doc import *
from validate import get_errors
import sys

class QDataViewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # Layout Init.
        self.language = 'ud'
        if len(sys.argv)>1:
            self.language = sys.argv[1]
        self.setGeometry(650, 300, 600, 600)
        self.setWindowTitle('Data Viewer')
        self.uploadButton = QPushButton('Load Conll File', self)
        self.sentence_id = 0
        self.column_number = 10
        self.columns = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD","DEPREL", "DEPS", "MISC"]
        self.current_dict = {}
        self.load_finished = True
        self.first_time = True
        self.map_col = {0:"ID", 1:"FORM", 2:"LEMMA", 3:"UPOS", 4:"XPOS", 5:"FEATS", 6:"HEAD", 7:"DEPREL", 8:"DEPS", 9:"MISC"}

        self.doc = None
        
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.uploadButton)
        self.setLayout(self.vBoxLayout)
        
        # Signal Init.
        self.connect(self.uploadButton, QtCore.SIGNAL('clicked()'), self.open)

    def open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', '.')[0]
        self.uploadButton.hide()
        print(filename)
        self.doc = Doc(filename)
        self.construct()

    def go_prev(self):
        self.doc.write()
        self.first_time = True
        if self.sentence_id>0:
            self.sentence_id-=1   
        self.update_table()
        self.update_html()
        self.check_errors()

        self.qTextEdit.setText(str(self.sentence_id))
        self.first_time = False
    
    def go_next(self):
        self.doc.write()
        self.first_time = True 
        if self.sentence_id<len(self.doc.sentences)-1:
            self.sentence_id+=1
        self.update_table()
        self.update_html()
        self.check_errors()

        self.qTextEdit.setText(str(self.sentence_id))
        self.first_time = False
    
    def go(self):
        self.doc.write()
        self.first_time = True 
        try:
            self.sentence_id = int(self.qTextEdit.toPlainText())
            self.update_table()
            self.update_html()
            self.check_errors()
        except Exception as e:
            print(e)
        
        self.qTextEdit.setText(str(self.sentence_id))
        self.first_time = False


    def construct(self):
        self.hBoxLayout = QHBoxLayout()
        self.prevButton = QPushButton("Prev", self)
        self.qTextEdit = QTextEdit()
        self.qTextEdit.setFixedHeight(30)
        self.qTextEdit.setFixedWidth(150)
        self.goButton = QPushButton("Go", self)
        self.nextButton = QPushButton("Next", self)
        self.hBoxLayout.addWidget(self.prevButton)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.qTextEdit)
        self.hBoxLayout.addWidget(self.goButton)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.nextButton)
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.chBoxLayout = QHBoxLayout()
        self.chBoxLayout.addStretch()
        cb_ids = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD","DEPREL", "DEPS", "MISC"]
        for cb_id in cb_ids:
            cb = QCheckBox(cb_id)
            cb.setChecked(True)
            cb.stateChanged.connect(self.cb_change)
            self.chBoxLayout.addWidget(cb)
        
        self.chBoxLayout.addStretch()
        self.vBoxLayout.addLayout(self.chBoxLayout)

        self.qTextEdit.setText(str(self.sentence_id))

        self.connect(self.prevButton, QtCore.SIGNAL('clicked()'), self.go_prev)
        self.connect(self.goButton, QtCore.SIGNAL('clicked()'), self.go)
        self.connect(self.nextButton, QtCore.SIGNAL('clicked()'), self.go_next)

        #create table here
        self.tableWidget = QTableWidget(self)
        self.update_table()
        self.tableWidget.itemChanged.connect(self.handle_change)
        self.vBoxLayout.addWidget(self.tableWidget)

        self.connect(self.tableWidget.verticalHeader(), QtCore.SIGNAL("sectionClicked(int)"), self.agg)

        self.errorList = QLabel(self)
        self.vBoxLayout.addWidget(self.errorList)
        
        
        self.webView = QWebEngineView()

        self.update_html()
        self.check_errors()
        self.vBoxLayout.addWidget(self.webView)

        self.webView.loadFinished.connect(self.finito)

        self.first_time = False
    
    def finito(self):
        self.load_finished = True
    
    def agg(self, x):
        
        if self.sentence.words[x].unitword:#remove two-words thing into one
            limit = int(self.sentence.words[x].id.split("-")[0])
            self.sentence.words[x].head = self.sentence.words[x+1].head
            self.sentence.words[x].lemma = self.sentence.words[x+1].lemma
            self.sentence.words[x].upos = self.sentence.words[x+1].upos
            self.sentence.words[x].xpos = self.sentence.words[x+1].xpos
            self.sentence.words[x].feats = self.sentence.words[x+1].feats
            self.sentence.words[x].deprel = self.sentence.words[x+1].deprel
            self.sentence.words[x].deps = self.sentence.words[x+1].deps
            self.sentence.words[x].misc = self.sentence.words[x+1].misc
            self.sentence.words[x].id = str(limit)
            self.sentence.words[x].unitword = False
            del self.sentence.words[x+1]
            del self.sentence.words[x+1]

            for word in self.sentence.words:
                if word.unitword:
                    x = int(word.id.split("-")[0])
                    if x>limit:
                        word.id = str(x-1)+"-"+str(x)
                else:
                    if int(word.id) > limit:
                        word.id = str(int(word.id)-1)
                
                if word.head != "_" and int(word.head) > limit:
                    word.head = str(int(word.head)-1)
            self.first_time = True
            self.update_table()
            self.update_html()
            self.first_time = False
        
        else:#add two-elements below
            base_word = self.sentence.words[x]
            limit = int(base_word.id)

            for word in self.sentence.words:
                if word.unitword:
                    x = int(word.id.split("-")[0])
                    if x>limit:
                        word.id = str(x+1)+"-"+str(x+2)
                else:
                    if int(word.id) > limit:
                        word.id = str(int(word.id)+1)
                
                if word.head != "_" and int(word.head) > limit:
                    word.head = str(int(word.head)+1)


            w1 = Word("\t".join([str(limit), base_word.form, base_word.lemma, base_word.upos, base_word.xpos, base_word.feats, base_word.head, base_word.deprel, base_word.deps, base_word.misc]), self.sentence.sent_address)
            w2 = Word("\t".join([str(limit+1), base_word.form, base_word.lemma, base_word.upos, base_word.xpos, base_word.feats, str(limit), base_word.deprel, base_word.deps, base_word.misc]), self.sentence.sent_address)
            self.sentence.words = self.sentence.words[:x+1]+[w1, w2]+self.sentence.words[x+1:]
            base_word.id = str(limit)+"-"+str(limit+1)
            base_word.lemma = "_"
            base_word.upos = "_"
            base_word.xpos = "_"
            base_word.feats = "_"
            base_word.head = "_"
            base_word.deprel = "_"
            base_word.deps = "_"
            base_word.misc = "_"
            base_word.unitword = True
            self.first_time = True
            self.update_table()
            self.update_html()
            self.first_time = False

    
    def update_table(self):
        self.sentence = self.doc.sentences[self.sentence_id]

        self.tableWidget.setRowCount(len(self.sentence.words))
        self.tableWidget.setColumnCount(self.column_number)
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        
        for enum, word in enumerate(self.sentence.words):
            if word.unitword:
                self.tableWidget.setVerticalHeaderItem(enum, QTableWidgetItem("-"))
            else:
                self.tableWidget.setVerticalHeaderItem(enum, QTableWidgetItem("+"))
            for i in range(self.column_number):
                if self.columns[i]=="ID":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.id))
                if self.columns[i]=="FORM":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.form))
                if self.columns[i]=="LEMMA":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.lemma))
                if self.columns[i]=="UPOS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.upos))
                if self.columns[i]=="XPOS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.xpos))
                if self.columns[i]=="FEATS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.feats))
                if self.columns[i]=="HEAD":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.head))
                if self.columns[i]=="DEPREL":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.deprel))
                if self.columns[i]=="DEPS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.deps))
                if self.columns[i]=="MISC":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.misc))
            
        self.tableWidget.resizeColumnsToContents()

    def check_errors(self):
        error_list = get_errors(self.sentence.get_raw(), self.sentence.sent_id, self.language)
        if len(error_list)>0:
            error_raw_string = 'ERRORS:\n'
            for error in error_list:
                error_raw_string+=error+'\n'
            self.errorList.setText(error_raw_string)
        else:
            self.errorList.setText('')
    def update_html(self):
        if not self.load_finished: #If the js function not loaded an image onto app it removes browser
            print("Load error!")
            self.vBoxLayout.removeWidget(self.webView)
            self.webView = QWebEngineView()
            self.webView.loadFinished.connect(self.finito)
            self.vBoxLayout.addWidget(self.webView)

    
        self.sentence = self.doc.sentences[self.sentence_id]
        
        html = process_document(self.sentence)
        self.webView.setHtml(html)
        self.load_finished = False


    def cb_change(self):
        self.column_number = 0
        self.columns = []
        self.map_col = {}
        x = 0
        for i in range(self.chBoxLayout.count()):
            if isinstance(self.chBoxLayout.itemAt(i), QWidgetItem):
                wid = self.chBoxLayout.itemAt(i).widget()
                if wid.isChecked():
                    self.columns.append(wid.text())
                    self.column_number += 1
                    self.map_col[x] = wid.text()
                    x+=1
                    
        self.first_time = True
        self.update_table()
        self.first_time = False
                

    def handle_change(self, item):

        text = item.text()
        #print(text)
        if text == "":
            text = "_"
        col = self.map_col[item.column()]
        row = item.row()
        self.sentence = self.doc.sentences[self.sentence_id]
        
        if col=="ID":
            self.sentence.words[row].id = text
        if col=="FORM":
            self.sentence.words[row].form = text
        if col=="LEMMA":
            self.sentence.words[row].lemma = text
        if col=="UPOS":
            self.sentence.words[row].upos = text
        if col=="XPOS":
            self.sentence.words[row].xpos = text
        if col=="FEATS":
            self.sentence.words[row].feats = text
        if col=="HEAD":
            self.sentence.words[row].head = text
        if col=="DEPREL":
            self.sentence.words[row].deprel = text
        if col=="DEPS":
            self.sentence.words[row].deps = text
        if col=="MISC":
            self.sentence.words[row].misc = text

        if not self.first_time:
            self.update_html()
            self.check_errors()



   

def main():
    app = QApplication(sys.argv)
    mw = QDataViewer()
    mw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()