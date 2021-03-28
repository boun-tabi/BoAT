import sys
from PySide2 import QtCore, QtGui
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHBoxLayout, QTextEdit, QHeaderView, QCheckBox, QWidgetItem, QShortcut
from PySide2.QtCore import Slot, Qt
from helper import process_document
import queue
from Doc import *
from validate import get_errors
import sys
import os
import copy

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
        self.columns = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC"]
        self.current_dict = {}
        self.load_finished = True
        self.first_time = True
        self.map_col = {0:"ID", 1:"FORM", 2:"LEMMA", 3:"UPOS", 4:"XPOS", 5:"FEATS", 6:"HEAD", 7:"DEPREL", 8:"DEPS", 9:"MISC", 10:"Abbr", 11:"Animacy", 12:"Aspect", 13:"Case",
                        14:"Clusivity", 15:"Definite", 16:"Degree", 17:"Echo", 18:"Evident", 19:"Foreign", 20:"Gender", 21:"Mood", 22:"NounClass", 23:"NumType", 24:"Number",
                        25:"Number[psor]", 26:"Person", 27:"Person[psor]", 28:"Polarity", 29:"Polite", 30:"Poss", 31:"PronType", 32:"Reflex", 33:"Register", 34:"Tense", 35:"VerbForm",
                        36:"Voice"}

        self.doc = None
        
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.uploadButton)
        self.setLayout(self.vBoxLayout)
        
        # Signal Init.
        self.connect(self.uploadButton, QtCore.SIGNAL('clicked()'), self.open)

    def open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', '.')[0]
        self.notename = "notes-"+filename.split("/")[-1].split(".")[0]+".txt"
        self.uploadButton.hide()
        print(filename)
        self.doc = Doc(filename)

        if not os.path.exists(self.notename):
            open(self.notename, "w").close()

        self.construct()

    def writeNotes(self):
        if self.qTextEdit2.toPlainText() != "Write your note here...":
            if self.qTextEdit2.toPlainText() == "":
                if str(self.sentence_id) in self.noteDictionary:
                    del self.noteDictionary[str(self.sentence_id)]
            else:
                self.noteDictionary[str(self.sentence_id)] = self.qTextEdit2.toPlainText().rstrip().replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
            noteTxt = open(self.notename, "w")
            for noteKey in sorted(self.noteDictionary.keys()):
                noteTxt.write(noteKey+" --- "+self.noteDictionary[noteKey]+"\n")
            noteTxt.close()

    def go_prev(self):
        self.doc.write()
        self.first_time = True
        self.writeNotes()

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
        self.writeNotes()

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
        self.writeNotes()

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
        self.prevButton.setShortcut("Alt+O")

        self.qTextEditAddRow = QTextEdit()
        self.qTextEditAddRow.setFixedHeight(20)
        self.qTextEditAddRow.setFixedWidth(60)

        self.qTextEditDeleteRow = QTextEdit()
        self.qTextEditDeleteRow.setFixedHeight(20)
        self.qTextEditDeleteRow.setFixedWidth(60)

        self.qTextEdit = QTextEdit()
        self.qTextEdit.setFixedHeight(20)
        self.qTextEdit.setFixedWidth(60)

        self.qTextEdit2 = QTextEdit()
        self.qTextEdit2.setFixedHeight(20)
        self.qTextEdit2.setFixedWidth(500)

        self.shortcutText=QShortcut(QtGui.QKeySequence("Alt+M"), self)
        self.shortcutText.activated.connect(self.qTextEdit2.setFocus)

        self.goButton = QPushButton("Go", self)
        self.nextButton = QPushButton("Next", self)
        self.nextButton.setShortcut("Alt+P")
        self.addRowButton = QPushButton("Add Row", self)
        self.deleteRowButton = QPushButton("Delete Row", self)
        self.hBoxLayout.addWidget(self.prevButton)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.qTextEditAddRow)
        self.hBoxLayout.addWidget(self.addRowButton)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.qTextEditDeleteRow)
        self.hBoxLayout.addWidget(self.deleteRowButton)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.qTextEdit)
        self.hBoxLayout.addWidget(self.goButton)

        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.qTextEdit2)

        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.nextButton)
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.chBoxLayout = QHBoxLayout()
        self.chBoxLayout.addStretch()
        cb_ids = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC"]
        cb_ids2 = ["Abbr", "Animacy", "Aspect", "Case", "Clusivity", "Definite", "Degree", "Echo", "Evident", "Foreign", "Gender", "Mood", "NounClass", "NumType"]
        cb_ids3 = ["Number", "Number[psor]", "Person", "Person[psor]", "Polarity", "Polite", "Poss", "PronType", "Reflex", "Register", "Tense", "VerbForm", "Voice"]
        for cb_id in cb_ids:
            cb = QCheckBox(cb_id)
            cb.setChecked(True)
            cb.stateChanged.connect(self.cb_change)
            self.chBoxLayout.addWidget(cb)
        
        self.chBoxLayout.addStretch()
        self.vBoxLayout.addLayout(self.chBoxLayout)

        self.chBoxLayout_2 = QHBoxLayout()
        self.chBoxLayout_2.addStretch()
        for cb_id in cb_ids2:
            cb = QCheckBox(cb_id)
            cb.setChecked(False)
            cb.stateChanged.connect(self.cb_change)
            self.chBoxLayout_2.addWidget(cb)

        self.chBoxLayout_2.addStretch()
        self.vBoxLayout.addLayout(self.chBoxLayout_2)

        self.chBoxLayout_3 = QHBoxLayout()
        self.chBoxLayout_3.addStretch()
        for cb_id in cb_ids3:
            cb = QCheckBox(cb_id)
            cb.setChecked(False)
            cb.stateChanged.connect(self.cb_change)
            self.chBoxLayout_3.addWidget(cb)

        self.chBoxLayout_3.addStretch()
        self.vBoxLayout.addLayout(self.chBoxLayout_3)

        self.qTextEdit.setText(str(self.sentence_id))

        self.noteDictionary = {}
        noteFile = open(self.notename, "r")
        for note in noteFile:
            noteSplitted = note.split(" --- ")
            noteID = noteSplitted[0]
            noteContent = noteSplitted[1].rstrip()
            self.noteDictionary[noteID] = noteContent
        noteFile.close()

        self.connect(self.prevButton, QtCore.SIGNAL('clicked()'), self.go_prev)
        self.connect(self.goButton, QtCore.SIGNAL('clicked()'), self.go)
        self.connect(self.nextButton, QtCore.SIGNAL('clicked()'), self.go_next)
        self.connect(self.addRowButton, QtCore.SIGNAL('clicked()'), self.add_row)
        self.connect(self.deleteRowButton, QtCore.SIGNAL('clicked()'), self.delete_row)

        #create table here
        self.tableWidget = QTableWidget(self)
        self.update_table()
        self.tableWidget.itemChanged.connect(self.handle_change)
        self.vBoxLayout.addWidget(self.tableWidget)

        self.connect(self.tableWidget.verticalHeader(), QtCore.SIGNAL("sectionClicked(int)"), self.agg)

        self.qTextEditError = QTextEdit()
        self.qTextEditError.setFixedHeight(40)
        self.qTextEditError.setFixedWidth(1115)
        self.qTextEditError.setReadOnly(True)
        self.vBoxLayout.addWidget(self.qTextEditError)

        
        self.webView = QWebEngineView()

        self.update_html()
        self.check_errors()
        self.vBoxLayout.addWidget(self.webView)

        self.webView.loadFinished.connect(self.finito)

        self.first_time = False
    
    def finito(self):
        self.load_finished = True

    def add_row(self):

        if "-" not in self.qTextEditAddRow.toPlainText():

            word_id = int(self.qTextEditAddRow.toPlainText())
            possible_move = True
            new_sentence_words = []

            for word in self.sentence.words:
                if word.unitword:
                    x1 = int(word.id.split("-")[0])
                    x2 = int(word.id.split("-")[1])
                    if word_id == x1 or word_id == x2:
                        possible_move = False

            if possible_move:
                for word in self.sentence.words:
                    new_word = copy.deepcopy(word)

                    if new_word.head != "_" and int(new_word.head) >= word_id:
                        new_word.head = str(int(new_word.head) + 1)

                    if new_word.unitword:
                        new_word_id = int(new_word.id.split("-")[0])
                    else:
                        new_word_id = int(new_word.id)

                    if new_word_id < word_id:
                        new_sentence_words.append(new_word)
                    elif new_word_id == word_id:
                        if new_word.unitword:
                            x1 = int(new_word.id.split("-")[0])
                            x2 = int(new_word.id.split("-")[1])
                            w = Word("\t".join(
                                [str(x1), new_word.form, "_", "_", "_", "_", new_word.head, "_", "_", "_"]), self.sentence.sent_address)
                            new_word.id = str(x1 + 1) + "-" + str(x2 + 1)
                        else:
                            w = Word("\t".join(
                                [new_word.id, new_word.form, "_", "_", "_", "_", new_word.head, "_", "_", "_"]), self.sentence.sent_address)
                            new_word.id = str(int(new_word.id) + 1)
                        new_sentence_words.append(w)
                        new_sentence_words.append(new_word)
                    elif new_word_id > word_id:
                        if new_word.unitword:
                            x1 = int(new_word.id.split("-")[0])
                            x2 = int(new_word.id.split("-")[1])
                            new_word.id = str(x1 + 1) + "-" + str(x2 + 1)
                        else:
                            new_word.id = str(int(new_word.id) + 1)
                        new_sentence_words.append(new_word)

                self.sentence.words = copy.deepcopy(new_sentence_words)
                self.first_time = True
                self.update_table()
                self.update_html()
                self.first_time = False

    def delete_row(self):

        if "-" not in self.qTextEditDeleteRow.toPlainText():

            word_id = int(self.qTextEditDeleteRow.toPlainText())
            possible_move = True
            new_sentence_words = []

            for word in self.sentence.words:
                if word.unitword:
                    x1 = int(word.id.split("-")[0])
                    x2 = int(word.id.split("-")[1])
                    if word_id == x1 or word_id == x2:
                        possible_move = False
                if not word.head == "_":
                    if int(word.head) == word_id:
                        possible_move = False

            if possible_move:
                for word in self.sentence.words:
                    new_word = copy.deepcopy(word)

                    if new_word.head != "_" and int(new_word.head) >= word_id:
                        new_word.head = str(int(new_word.head) - 1)

                    if new_word.unitword:
                        new_word_id = int(new_word.id.split("-")[0])
                    else:
                        new_word_id = int(new_word.id)

                    if new_word_id < word_id:
                        new_sentence_words.append(new_word)
                    elif new_word_id > word_id:
                        if new_word.unitword:
                            x1 = int(new_word.id.split("-")[0])
                            x2 = int(new_word.id.split("-")[1])
                            new_word.id = str(x1 - 1) + "-" + str(x2 - 1)
                        else:
                            new_word.id = str(int(new_word.id) - 1)
                        new_sentence_words.append(new_word)

                self.sentence.words = copy.deepcopy(new_sentence_words)
                self.first_time = True
                self.update_table()
                self.update_html()
                self.first_time = False

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
                    first_word_id = int(word.id.split("-")[0])
                    if first_word_id>limit:
                        word.id = str(first_word_id-1)+"-"+str(first_word_id)
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
                    first_word_id = int(word.id.split("-")[0])
                    if first_word_id>limit:
                        word.id = str(first_word_id+1)+"-"+str(first_word_id+2)
                else:
                    if int(word.id) > limit:
                        word.id = str(int(word.id)+1)
                
                if word.head != "_" and int(word.head) > limit:
                    word.head = str(int(word.head)+1)


            w1 = Word("\t".join([str(limit), base_word.form, base_word.lemma, base_word.upos, base_word.xpos, base_word.feats, base_word.head, base_word.deprel, base_word.deps, "_"]), self.sentence.sent_address)
            w2 = Word("\t".join([str(limit+1), base_word.form, base_word.lemma, base_word.upos, base_word.xpos, base_word.feats, str(limit), base_word.deprel, base_word.deps, "_"]), self.sentence.sent_address)
            self.sentence.words = self.sentence.words[:x+1]+[w1, w2]+self.sentence.words[x+1:]
            base_word.id = str(limit)+"-"+str(limit+1)
            base_word.lemma = "_"
            base_word.upos = "_"
            base_word.xpos = "_"
            base_word.feats = "_"
            base_word.head = "_"
            base_word.deprel = "_"
            base_word.deps = "_"
            base_word.unitword = True
            self.first_time = True
            self.update_table()
            self.update_html()
            self.first_time = False

    
    def update_table(self):
        if str(self.sentence_id) in self.noteDictionary:
            self.qTextEdit2.setText(self.noteDictionary[str(self.sentence_id)])
        else:
            self.qTextEdit2.setText("Write your note here...")

        self.sentence = self.doc.sentences[self.sentence_id]

        self.tableWidget.setRowCount(len(self.sentence.words))
        self.tableWidget.setColumnCount(self.column_number)
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        
        for enum, word in enumerate(self.sentence.words):
            if word.unitword:
                self.tableWidget.setVerticalHeaderItem(enum, QTableWidgetItem("-"))
            else:
                self.tableWidget.setVerticalHeaderItem(enum, QTableWidgetItem("+"))

            dict_feat = {}
            uni_feats = re.split('\|', word.feats)
            if uni_feats[0] != "_":
                for uni_feat in uni_feats:
                    uf = re.split('\=', uni_feat)
                    dict_feat[uf[0]]=uf[1]

            for i in range(self.column_number):
                if self.columns[i]=="ID":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.id))
                elif self.columns[i]=="FORM":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.form))
                elif self.columns[i]=="LEMMA":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.lemma))
                elif self.columns[i]=="UPOS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.upos))
                elif self.columns[i]=="XPOS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.xpos))
                elif self.columns[i]=="FEATS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.feats))
                elif self.columns[i]=="HEAD":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.head))
                elif self.columns[i]=="DEPREL":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.deprel))
                elif self.columns[i]=="DEPS":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.deps))
                elif self.columns[i]=="MISC":
                    self.tableWidget.setItem(enum, i, QTableWidgetItem(word.misc))
                else:
                    if self.columns[i] in dict_feat:
                        self.tableWidget.setItem(enum, i, QTableWidgetItem(dict_feat[self.columns[i]]))
                    else:
                        self.tableWidget.setItem(enum, i, QTableWidgetItem("_"))
            
        self.tableWidget.resizeColumnsToContents()

    def check_errors(self):
        error_list = get_errors(self.sentence.get_raw(), self.sentence.sent_id, self.language)
        if len(error_list)>0:
            error_raw_string = 'ERRORS:\n'
            for error in error_list:
                error_raw_string+=error+'\n'
            self.qTextEditError.setText(error_raw_string)
        else:
            self.qTextEditError.setText('')
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
        for i in range(self.chBoxLayout_2.count()):
            if isinstance(self.chBoxLayout_2.itemAt(i), QWidgetItem):
                wid = self.chBoxLayout_2.itemAt(i).widget()
                if wid.isChecked():
                    self.columns.append(wid.text())
                    self.column_number += 1
                    self.map_col[x] = wid.text()
                    x+=1
        for i in range(self.chBoxLayout_3.count()):
            if isinstance(self.chBoxLayout_3.itemAt(i), QWidgetItem):
                wid = self.chBoxLayout_3.itemAt(i).widget()
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
        elif col=="FORM":
            self.sentence.words[row].form = text
        elif col=="LEMMA":
            self.sentence.words[row].lemma = text
        elif col=="UPOS":
            self.sentence.words[row].upos = text.upper()
        elif col=="XPOS":
            self.sentence.words[row].xpos = text
        elif col=="FEATS":
            self.sentence.words[row].feats = text
        elif col=="HEAD":
            self.sentence.words[row].head = text
        elif col=="DEPREL":
            self.sentence.words[row].deprel = text
        elif col=="DEPS":
            self.sentence.words[row].deps = text
        elif col=="MISC":
            self.sentence.words[row].misc = text
        else:
            cur_col = col
            if col=="Number[psor]":
                cur_col = "Number\[psor\]"
            if col=="Person[psor]":
                cur_col = "Person\[psor\]"
            if (re.search(cur_col+'=\w*', self.sentence.words[row].feats) is None) and (text!="_"):
                if self.sentence.words[row].feats=="_":
                    self.sentence.words[row].feats = col+"="+text
                else:
                    sorted_feats = re.split('\|', self.sentence.words[row].feats)
                    match_col=""
                    match_val=""
                    for sorted_feat in sorted_feats:
                            sf = re.split('\=', sorted_feat)
                            if sf[0]<col:
                                match_col = sf[0]
                                match_val = sf[1]
                    if match_col=="":
                        self.sentence.words[row].feats = col+"="+text+"|"+self.sentence.words[row].feats
                    else:
                        cur_match_col=match_col
                        if match_col == "Number[psor]":
                            cur_match_col = "Number\[psor\]"
                        if match_col == "Person[psor]":
                            cur_match_col = "Person\[psor\]"
                        self.sentence.words[row].feats = re.sub(cur_match_col+'='+match_val, match_col+'='+match_val+"|"+col+"="+text, self.sentence.words[row].feats)
            else:
                self.sentence.words[row].feats = re.sub(cur_col+'=\w*', col+"="+text, self.sentence.words[row].feats)

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