import re

class Doc:
    def __init__(self, filepath):    
        SENTENCE_SPLIT = r"\n\n+"
        DOC_ID = r"newdoc id\s*=\s*(\w+)\s*$"
        SENT_ID = r"sent_id\s*=\s*(.+)\s*$"
        TEXT = r"text\s*=\s*(.+)\s*$"
            
        with open(filepath, "r", encoding = "utf-8") as f:
            content = f.read()
        content = content[content.find("\n")+1:]
        
        self.filepath = filepath
        self.sentences = []
        
        sents = re.split(SENTENCE_SPLIT, content)
        for sentence_id, sentence in enumerate(sents):
            sentence = sents[sentence_id]
            
            sent_id = "not_found"
            m = re.search(SENT_ID, sentence, flags=re.MULTILINE)
            if m:
                sent_id = m.group(1)
            
            doc_id = "not_found"
            m = re.search(DOC_ID, sentence, flags=re.MULTILINE)
            if m:
                doc_id = m.group(1)

            text = "not_found"
            m = re.search(TEXT, sentence, flags=re.MULTILINE)
            if m:
                text = m.group(1)
            

            #removes hashtagged lines
            empty_lines = 0
            for l in sentence.splitlines():
                if not l.startswith("#"):
                    break
                empty_lines+=1

            words = sentence.splitlines()[empty_lines:]
            
            self.sentences.append(Sentence(doc_id, sent_id, text, words))


    def write(self):
        content = ""
        for sentence in self.sentences:
            content += "# sent_id = "+sentence.sent_id+"\n"
            content += "# text = "+sentence.text+"\n"
            for word in sentence.words:
                content += "\t".join(word.get_list())+"\n"
            content+="\n"
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)



class Sentence:
    def __init__(self, doc_id, sent_id, text, words):
        self.text = text
        self.sent_id = sent_id
        self.sent_address = "n"+str(sent_id)
        self.doc_id = doc_id
        self.words = []
        for word in words:
            w = Word(word, self.sent_address)
            self.words.append(w)
        
    def get_head(self):
        for word in self.words:
            if word.head == "0":
                return word.address()
        return "Null"


class Word:
    def __init__(self, word, sa):
        items = word.split("\t")
        
        self.sent_add = sa
        self.id = items[0]
        self.form = items[1]
        self.lemma = items[2]
        self.upos = items[3]
        self.xpos = items[4]
        self.feats = items[5]
        self.head = items[6]
        self.deprel = items[7]
        self.deps = items[8]
        self.misc = items[9]
        self.unitword = False
        if "-" in self.id:
            self.unitword = True
    
    def get_list(self):
        return [self.id, self.form, self.lemma, self.upos, self.xpos, self.feats, self.head, self.deprel, self.deps, self.misc]
    
    
    def address(self):
        return self.sent_add+"-"+self.id