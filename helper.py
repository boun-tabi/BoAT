

def process_document(sentence):
    jquery = 'https://code.jquery.com/jquery-2.1.4.min.js'
    fsaver = 'https://cdn.rawgit.com/eligrey/FileSaver.js/1.3.4/FileSaver.min.js'
    js_t_v = 'https://cdn.rawgit.com/ufal/js-treex-view/gh-pages/js-treex-view.js'
    output = """
            <style>
            .center {
            margin: 0;
            position: absolute;
            left: 50%;
            -ms-transform: translate(-50%, 0%);
            transform: translate(-50%, 0%);
            }
            </style>
            """
    for js_file in (jquery, fsaver, js_t_v):
        output += ('<script src="%s"></script>' % js_file)+"\n"
    
    output += ('<div id="treex-view" class="center"></div><script>\n')
    output += 'data=[\n'
    output += '{"zones":{'
    desc = ''
 
    #print("#######################")
    # TODO: if not self._should_process_tree(tree): continue
    output += '"' '":{"sentence":"'+_esc(sentence.text)+'",'
    output += '"trees":{"a":{"language":"''","nodes":['+'\n'
    output += '{"id":"'+sentence.sent_address+'","parent":null,'
    output += '"firstson":"' + (sentence.get_head() if sentence.words else None)+'",'
    output += '"labels":["zone=' '","id='+sentence.sent_id+'"]}'+"\n"
    desc += ',["[' ']","label"],[" ","space"]' + "\n"
    first_word_id = ""
    second_word_id = ""
    unitword_misc = ""
    for word in sentence.words:
        if word.unitword:
            first_word_id = word.id.split("-")[0]
            second_word_id = str(int(first_word_id) + 1)
            unitword_misc = word.misc
        if not word.unitword:
            res = print_node(sentence, word, first_word_id, second_word_id, unitword_misc)
            desc += res[0]
            output += res[1]
    desc += r',["\n","newline"]'
    output += (']}}}')+"\n"
    output += '},"desc":['+desc[1:]+']}'+"\n"
    # print desc without the extra starting comma
    output += ('];\n')
    output += ("$('#treex-view').treexView(data);\n")
    output += ('</script>')
    
    return output

def _esc(string):
    if string is None:
        string = ''
    return string.replace('\\', '\\\\').replace('"', r'\"')



def print_node(sentence, word, first_word_id, second_word_id, unitword_misc):
    """JSON representation of a given node."""
    output = ""
    # pylint does not understand `.format(**locals())` and falsely alarms for unused vars
    # pylint: disable=too-many-locals,unused-variable
    
    order, misc, form, lemma, upos, xpos, feats, deprel = [_esc(str(x)) for x in [word.id, word.misc, word.form, word.lemma, word.upos, word.xpos, word.feats, word.deprel]]
    address = str(sentence.sent_id)+"#"+str(word.id)
    id_node = '"'+word.address()+'"'

    if str(word.head) == "0":
        id_parent = '"'+sentence.sent_address+'"'
    elif str(word.head) == "_":
        id_parent = None
    else:
        ind = int(word.head)-1
        head_temp = sentence.words[ind]     
        while str(head_temp.id) != str(word.head):
            ind += 1
            head_temp = sentence.words[ind]
        
        if str(head_temp.id) == str(word.head):
            id_parent = '"'+head_temp.address()+'"'
        else:
            id_parent = None
    
    firstson_str = ''

    for temp_word in sentence.words:
        if word.id == temp_word.head:
            firstson_str = '"firstson":"'+str(temp_word.address())+'",'
            break
    
    rbrother_str = ''

    for temp_word in sentence.words:
        try:
            if int(temp_word.id) < int(word.id) or temp_word.id == word.id:
                continue
        except:
            continue
        if word.head == temp_word.head:
            rbrother_str = '"rbrother":"'+str(temp_word.address())+'",'
            break
        
    multiline_feats = feats.replace('|', r'\n')
    output += (',{{"id":{id_node},"parent":{id_parent},"order":{order},{firstson_str}{rbrother_str}'
            '"data":{{"ord":{order},"form":"{form}","lemma":"{lemma}","upos":"{upos}",'
            '"xpos":"{xpos}","feats":"{feats}","deprel":"{deprel}",'  # TODO: deps
            '"misc":"{misc}","id":"{address}"}},'
            '"labels":["{form}","#{{#bb0000}}{upos}","#{{#0000bb}}{deprel}"],'
            '"hint":"lemma={lemma}\\n{multiline_feats}"}}'.format(**locals()))+"\n"
    desc = ',["{form}",{id_node}]'.format(**locals())
    desc += ',[" ","space"]' if ('SpaceAfter=No' not in misc) and ((word.id != first_word_id) and ((word.id != second_word_id) or ((word.id == second_word_id) and (unitword_misc != 'SpaceAfter=No')))) else ''
    # pylint: enable=too-many-locals,unused-variable
    return (desc, output)

