#! /usr/bin/python3

# https://www.bibtex.com/e/entry-types/
labels = [ 'type', 'title', 'author', 'booktitle', 'journal', 'publisher', 'howpublished', 'organization', 'institution', 'address', 'editor', 'year', 'month', 'volume', 'number', 'series', 'pages', 'school', 'issn', 'doi', 'file', 'keywords', 'abstract', 'note' ]
itype       = labels.index('type')
ititle      = labels.index('title')
iauthor     = labels.index('author')
ijournal    = labels.index('journal')
iyear       = labels.index('year')
idoi        = labels.index('doi')
ifile       = labels.index('file')
ikeywords   = labels.index('keywords')
iabstract   = labels.index('abstract')
inote       = labels.index('note')
ikey = -1

blank  = ['']*len(labels)
unknown= ['?']*len(labels)
bheight= [ 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 1 ]

fields = {}
fields['article']       = [ 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1]
fields['book']          = [ 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1]
fields['booklet']       = [ 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1]
fields['inbook']        = [ 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1]
fields['incollection']  = [ 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1]
fields['inproceedings'] = [ 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1]
fields['manual']        = [ 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
fields['mastersthesis'] = [ 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1]
fields['misc']          = [ 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1] # note is expected here
fields['phdthesis']     = [ 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1]
fields['proceedings']   = [ 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1]
fields['techreport']    = [ 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1]
fields['unpublished']   = [ 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
fields['software']      = [ 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1] # made from misc and techreport

curbib = ''
curref = ''

import os, glob, sys
from jabbrev import journal_abbrev
from texconvert import texconvert
from bibcite import out_fmtrefs
from tkinter import *
from tkinter.simpledialog import askstring
from tkinter.filedialog   import askopenfilename, asksaveasfilename, askdirectory

bg='black'
fg='white'

userbibfile = ''
collections = {}    # directories
bibnames = {}       # bibfiles
references = {}     # citations
show = {}
show[''] = True
basedir = os.environ['HOME']+'/.local/share/bibmanager'
if not os.path.exists(basedir):
    os.mkdir(basedir)

def read_collections():
    if not os.path.exists(basedir+'/collections.dat'):
        return
    fileID = open(basedir+'/collections.dat')
    col = ''
    for line in fileID.readlines():
        if col not in collections:
            collections[col] = []
            if col not in show: show[col] = False
        if not line.strip():
            continue
        if line and line[0] == '#':
            col = line.strip('# \n')
        else:
            bib = col+'/'+line.split('\t')[0]
            collections[col].append(bib)
            bibnames[bib] = list(set( line.split('\t')[1].split() )) # remove eventual duplicates
            if len(bibnames[bib]) != len(line.split('\t')[1].split()): print(bib, 'had duplicates!')
    fileID.close()

def set_orphan():
    bibnames['/orphan'] = list(references)
    for col in collections:
        for bib in collections[col]:
            for ref in bibnames[bib]:
                if ref in bibnames['/orphan']:
                    bibnames['/orphan'].remove(ref)

def add_orphan(ref):
    found = False
    for col in collections:
        for bib in collections[col]:
            if ref in bibnames[bib]:
                found = True
                break
        if found: break
    if not found:
        bibnames['/orphan'].append(ref)

def read_bibfile(bibfile=''):
    add = False
    if not bibfile:
        bibfile = basedir+'/references.bib'
        bibname = ''
    else:
        colname = ''
        if curbib and curbib != 'search':
            colname = curbib.split('/')[0]
        bibname = '/'.join( [colname, bibfile.split('/')[-1]] )
        collections[colname].append(bibname)
        if bibname not in bibnames:
            bibnames[bibname] = []
        add = True
    if not os.path.exists(bibfile): return
    fileID = open(bibfile)
    for line in fileID.readlines():
        if line and line[0] == '@':
            btype = line.split('{')[0].strip('@').lower()
            ref = line.split('{')[-1].strip(', \n')
            if add:
                ref = valid_key(ref.lower())
                bibnames[bibname].append(ref)
            references[ref] = list(blank)
            references[ref][itype] = btype
        for idx in range(1,len(labels)):    # don't need to search for 'type'
            if line.strip() and line.split()[0].strip('=').lower().replace('issue','number') == labels[idx]:
                references[ref][idx] = '='.join(line.split('=')[1:]).strip(' ,\n')    # [1:-1]
                references[ref][idx] = references[ref][idx][1:-1]   # strip surrounding braces or quotes
                break
    fileID.close()
    return bibname

def valid_key(key):
    suffixes = ['']+list('abcdefghijklmnopqrstuvwxyz1234567890')
    for suf in suffixes:
        if key+suf not in references:
            return key+suf
    for suf in suffixes:
        return valid_key(key+suf)   # recursive

def get_keywords():
    global keywords
    keywords = {}
    for ref in references:
        for key in references[ref][ikeywords].replace(';',',').split(','):#.replace('/',',')
            key=key.lower().strip()
            if key not in keywords:
                keywords[key] = 0
            keywords[key] += 1

def set_kmenu():
    kidx=0
    kmenu.delete(0,'end')   # menu.delete(start_item_ix, menu.index(tk.END))
    while len(keywords) > kidx*30:
        kkmenu = Menu(kmenu)
        lab0=sorted(list(keywords))[kidx*30][:10]
        for key in sorted(list(keywords))[kidx*30:(kidx+1)*30]:
            kkmenu.add_command(label=key+' ('+str(keywords[key])+')',  command=lambda arg=key.lower():do_key(arg))
            lab1=key[:10]
        pre = ' '*int(1.6*(10-len(lab0)))
        kmenu.add_cascade(label=pre+lab0+'..->'+lab1+'..', menu=kkmenu)
        kidx += 1

def short_export():
    bexport(short=True)

def bexport(bib='', short=False):
    if not bib:
        if not curbib: return
        bib = curbib
    bibfile = asksaveasfilename()
    if not bibfile: return
    save_bibs(bib, bibfile, short)

def copy_bib(bib):
    oldcol, oldbib = bib.split('/')
    arg = askstring('', 'name a new bibliography or a collection:')
    if not arg: return
    if arg in collections:
        newcol = arg
        newbib = newcol+'/'+oldbib
    else:
        newcol = oldcol
        newbib = newcol+'/'+arg
    collections[newcol].append(newbib)
    bibnames[newbib] = []
    for ref in bibnames[bib]:
        bibnames[newbib].append(ref)
    show_collections()

filteredbib = ''
def do_filter(event):
    global filteredbib
    filterstr = fentry.get().lower().split()
    bibnames['search'] = []
    if curbib != 'search': filteredbib = curbib
    if filteredbib:
        keys = bibnames[filteredbib]
    else: keys = list(references)
    for key in keys:
        found = True
        if ftype['text'] in fields and ftype['text'] != references[key][itype]: #!= 'type'
            found = False
        elif filterstr:
          for flt in filterstr:
            if  not (ckauth.get()  and flt in references[key][iauthor].lower()) \
            and not (cktitl.get()  and flt in references[key][ititle].lower())   \
            and not (ckkeyw.get()  and flt in references[key][ikeywords].lower()) \
            and not (flt.isdigit() and flt in references[key][iyear]):
                found = False
        if found:
            bibnames['search'].append(key)
    show_bib('search')

def do_key(keyword):
    bibnames['search'] = []
    for key in references:
#       if keyword in references[key][ikeywords].lower():   # faster, but renders false positive
        for k in references[key][ikeywords].split(','):
            if keyword == k.strip().lower():
                bibnames['search'].append(key)
    show_bib('search')

def find_dup(bib=''):
    if not bib:
        data = list(references)
    else:
        data = bibnames[bib]
    bibnames['search'] = []
    for idx0 in range(len(references)):
        if idx0 >= len(references): # if an item was removed from references
            break
        key0 = list(references)[idx0]
        if not bib: idx1=idx0+1
        else:       idx1=0
        for ref1 in data[idx1:]:
            if ref1==ref0: continue
            if ref0 not in references or ref1 not in references: continue   # already merged
            if references[ref0][idoi] and references[ref1][idoi] and references[ref0][idoi].lower() == references[ref1][idoi].lower():
                merge(ref0, ref1)
                continue
            if not references[ref0][iauthor] or not references[ref1][iauthor]: continue
            if not references[ref0][ititle]  or not references[ref1][ititle]:  continue
            if not references[ref0][iyear]   or not references[ref1][iyear]:   continue
            if references[ref0][iauthor].lower().split()[0]      == references[ref1][iauthor].lower().split()[0] \
                and references[ref0][ititle].lower().split()[:2] == references[ref1][ititle].lower().split()[:2] \
                and references[ref0][iyear]                      == references[ref1][iyear]:
                    if ref0 not in bibnames['search']: bibnames['search'].append(ref0)
                    if ref1 not in bibnames['search']: bibnames['search'].append(ref1)
    show_bib('search')
    set_multiple()

def bmerge():
    indexes = area2.curselection()
    if len(indexes) < 2: return
    ref0 = sorted(bibnames[curbib])[indexes[0]]
    for idx in range(1,len(indexes)):
        ref1 = sorted(bibnames[curbib])[indexes[idx]]
        merge(ref0, ref1)

def merge(ref0, ref1):
    print('merging:', ref0, 'and', ref1)
    keep = min(ref0, ref1)
    excl = max(ref0, ref1)
    for idx in range(len(labels)):
        if not references[keep][idx]:
            references[keep][idx] = references[excl][idx]
    del references[excl]
    for bib in bibnames:
        if excl in bibnames[bib]:
            bibnames[bib].remove(excl)
            if bib == 'search':
                bibnames[bib].remove(keep)
            elif keep not in bibnames[bib]:
                bibnames[bib].append(keep)
        if bib == curbib:
            show_bib(bib)
    show_bib()
    show_ref(keep)

def bimport():
    arg = askopenfilename(filetypes = [('bib files', ('*.bib'))] )
    if not arg: return
    bibname = read_bibfile(arg) #, bib=bibname)
    show_collections()
    find_dup(bibname)           # will show duplicated results in 'search'
    if not bibnames['search']:  # if no dup found
        show_bib(bibname)

def set_type(arg):
    bvalues[0]['text'] = arg
    for idx in range(len(labels)):
        bvalues[idx]['state'] = 'normal'
        if not fields[arg][idx]:
            bvalues[idx]['state'] = 'disabled'

def set_ftype(arg):
    if arg:
        ftype['text'] = arg
    else:
        ftype['text'] = 'type'
    do_filter('')

def get_file(event):
    arg = askopenfilename()
    if arg:
        bvalues[ifile].delete(0,'end')
        bvalues[ifile].insert(0,arg) #.replace(papersdir,''))
        print('<-', arg)

def move_file(event):
    arg = askdirectory()
    if arg:
        oldfile = bvalues[ifile].get()
        newfile = arg+'/'+oldfile.split('/')[-1]
        print(oldfile, '->', arg)
        os.path.rename(oldfile, newfile)
        bvalues[ifile].delete(0,'end')
        bvalues[ifile].insert(0,newfile) #.replace(papersdir,''))

def toggle_mode():
    if mmode['relief'] == SUNKEN: set_browse()
    else:                         set_multiple()
def set_multiple():
    mmode['relief'] = SUNKEN
    area2['selectmode'] = 'multiple'
def set_browse():
    mmode['relief'] = RAISED
    area2['selectmode'] = 'browse' #'single'

def has_ref(e):
    print('up', e.char)
def hide_ref(e):
    print('down', e.char)

def do_gui():
    global fentry, area0, area1, area2, bvalues, scroll1, scroll2, ckauth, cktitl, ckkeyw, mmode, kmenu, ftype
    topbar = Frame(app)
    topbar.pack(fill=X)
    Button(topbar, text='import bib', relief='flat', command=bimport).pack(side='left')
    ebutton = Menubutton(topbar, text='export bib', padx=5, pady=5, relief='flat') #'raised')
    emenu = Menu(ebutton, tearoff=False)
    emenu.add_command(label='short journal names', command=short_export)
    emenu.add_command(label='long journal names',  command=bexport)
    ebutton['menu'] = emenu
    ebutton.pack(side='left')

    rbutton = Menubutton(topbar, text='→references', padx=5, pady=5, relief='flat') #'raised')
    rmenu = Menu(rbutton, tearoff=False)
    for fname in glob.glob(basedir+'/*.sty'):
        rmenu.add_command(label=fname.replace(basedir,'').strip('/'), command=lambda arg=fname: write_fmtrefs(arg))
    rbutton['menu'] = rmenu
    rbutton.pack(side='left')

    kbutton = Menubutton(topbar, text='keywords', padx=5, pady=5, relief='flat')
    kmenu = Menu(kbutton, tearoff=False)
    kbutton['menu'] = kmenu
    kbutton.pack(side='left')

    fentry = Entry(topbar)
    fentry.pack(fill=X, expand=True, side='left')
    fentry.bind('<Return>', do_filter)
    ckauth = IntVar()
    cktitl = IntVar()
    ckkeyw = IntVar()
    Checkbutton(topbar, text='authors',  variable=ckauth).pack(side='left')   #
    Checkbutton(topbar, text='title',    variable=cktitl).pack(side='left')   #
    Checkbutton(topbar, text='keywords', variable=ckkeyw).pack(side='left')   #
    ckauth.set(1)
    cktitl.set(1)
    ftype = Menubutton(topbar, text='type')
    tMenu = Menu(ftype) #, tearoff=False)
    for label in ['']+list(fields):
        tMenu.add_command(label=label, command=lambda arg=label: set_ftype(arg))
    ftype['menu'] = tMenu
    ftype.pack(side='left') #fill=X, expand=True, 
    mmode = Button(topbar, text='select', command=toggle_mode)#, relief=FLAT
    mmode.pack(side='left')
    Button(topbar, text='duplicates', relief='flat', command=find_dup).pack(side='left')
    Button(topbar, text='🗀', relief='flat', command=save_bibs).pack(side='left') # 🗀 📁 🖫 ↓ ⭳↧
    Button(topbar, text='🗙', relief='flat', command=app_quit).pack(side='left')
    main = Frame(app)
    main.pack(fill='both',expand=True)
    area0 = Frame(main)
    area0.pack(fill='both', expand=True, side='left')
    area1 = Frame(area0)
    area1.pack(fill=Y, side='left')
    scroll1 = Scrollbar(area0)
    area2 = Frame(area0) #, width=800)
    area2.pack(fill='both', side='left')
    scroll2 = Scrollbar(area0)
    area3 = Frame(main)
    area3.pack(fill='both', side='right')
    bvalues = []    # bframes and bvalues will have the same indexes of labels[], but one more item for the 'key' value,
    bframes = []    # which is the last defined item, and the first shown one
    bframes.append(Frame(area3))
    bvalues.append( Menubutton(bframes[-1], relief='raised', text='type') )
    bMenu = Menu(bvalues[-1])
    for label in fields:
        bMenu.add_command(label=label, command=lambda arg=label: set_type(arg))
    bvalues[-1]['menu'] = bMenu
    bvalues[-1].pack(side='left') #fill=X, expand=True, 
    bframes[-1].pack(fill=X)
    for idx in range(1,len(labels)):
        bframes.append(Frame(area3))
        text = (labels+['key'])[idx]
        if text=='number': text='number/issue'
        Label(bframes[idx], text=text).pack(side='left')
        if bheight[idx] > 1: #== ititle or idx == iauthor:
            bvalues.append( Text(bframes[idx], height=bheight[idx]) )#, width=40
            if idx==iabstract:
                bvalues[-1].bind('<Control-Return>', lambda event: get_abstract())
            else: bvalues[-1].bind('<Control-Return>', lambda event,arg=idx: format_title(arg))
        else:
            bvalues.append( Entry(bframes[idx]) )
            if idx == ifile:
                bvalues[idx].bind('<Button-1>', get_file)
                bvalues[idx].bind('<Control-Return>', ren_file)
                bvalues[idx].bind('<Button-3>', open_file)
                bvalues[idx].bind('<Control-Button-1>', move_file)
            elif idx == idoi:
                bvalues[idx].bind('<Control-Return>', parse_ref_doi)
                bvalues[idx].bind('<Button-3>', open_doi)
            else: bvalues[-1].bind('<Control-Return>', lambda event,arg=idx: format_title(arg))
        bvalues[-1].pack(fill=X, expand=True, side='left')
        bvalues[ikey].bind('<Return>', lambda event: update_bib())
        bframes[idx].pack(fill=X)
        if idx == ifile:
            bvalues[idx].bind('<FocusOut>', lambda event: valid_file())   # <KeyPress>
        elif idx != itype and idx != ifile:
            bvalues[idx].bind('<KeyRelease>', lambda event,arg=idx: valid_braces(arg))   # <KeyPress>
    bvalues.append( Entry(bframes[0]) )
    bvalues[-1].pack(fill=X, expand=True, side='left')
    bvalues[ikey].bind('<Return>', format_key)
    Button(area3, text='edit all fields', command=activate_fields).pack(fill=X)
    show_collections()

def show_collections():
    global area1, scroll1, area2, collist
    area1.pack_forget()
    scroll1.pack_forget()
    scroll1 = Scrollbar(area0)
    area1 = Listbox(area0, exportselection=False, yscrollcommand=scroll1.set)
    area1.pack(side='left',fill=Y)
    scroll1.pack(side='left', fill=Y)
    scroll1.config(command=area1.yview)

    collist = []
    for collection in sorted(collections):
        collist.append(collection)
        if show[collection]:
            area1.insert(END, 'v '+collection)
            for bib in sorted(collections[collection]):
                area1.insert(END, '    '+bib.split('/')[-1]+' (%d)'%len(bibnames[bib]))
                collist.append(bib)
        else:
            area1.insert(END, '> '+collection)
    area1.insert(END, 'orphan')
    collist.append('/orphan')
    def colselect(event):
        if not event.widget.curselection(): return
        index = int(event.widget.curselection()[0])
        for idx in range(len(collist)):
            area1.itemconfig(idx,bg='')
        item = collist[index] #event.widget.get(index)
        if '/' in item: show_bib(item)
        else:
            show[item] = not show[item]
            show_collections()
    def context(event):
        widget = event.widget
        index = widget.nearest(event.y)
        _, yoffset, _, height = widget.bbox(index)
        cmenu = Menu(area1, tearoff=0)
        if event.y > height + yoffset + 5: # XXX 5 is a niceness factor :)
            index = 0
        widget.selection_clear(0,'end')
        widget.selection_set(index) # widget.activate(index)
        item = collist[index] #widget.get(index)
        if not index:
            cmenu.add_command(label='add col', command=add_col)
            cmenu.add_command(label='add bib', command=lambda arg=item: add_bib(arg))
        else:
            if '/' not in item:
                cmenu.add_command(label='rename col', command=lambda arg=item: ren_col(arg))
                cmenu.add_command(label='remove col', command=lambda arg=item: rem_col(arg))
                cmenu.add_command(label='add bib', command=lambda arg=item: add_bib(arg))
            else:
                cmenu.add_command(label='add ref', command=lambda arg=item: add_ref(arg))
                mvmenu = Menu(cmenu)
                for col in collections:
                    if col != collection:
                        mvmenu.add_command(label=''+col, command=lambda arg0=item,arg1=col: mov_bib(arg0,arg1))
                cmenu.add_cascade(label='move bib', menu=mvmenu)
                cmenu.add_command(label='rename bib', command=lambda arg=item: ren_bib(arg))
                cmenu.add_command(label='remove bib', command=lambda arg=item: rem_bib(arg))
                cmenu.add_command(label='copy bib', command=lambda arg=item: copy_bib(arg))
                cmenu.add_command(label='export', command=lambda arg=item: bexport(arg))
        cmenu.post(event.x_root, event.y_root)
        cmenu.grab_set()
    area1.bind('<<ListboxSelect>>', colselect)
    area1.bind('<Button-3>', context)
    area2.pack_forget()
    area2 = Listbox(area0, yscrollcommand=scroll2.set)#, width=95
    area2.pack(fill='both', expand=True, side='left')
    if curbib: show_bib(curbib)

def mov_bib(bib, newcol):
    global curbib
    col    = bib.split('/')[0]
    newbib = newcol+'/'+bib.split('/')[-1]
    collections[col].remove(bib)
    collections[newcol].append(newbib)
    if bib == curbib: curbib = newbib
    bibnames[newbib] = bibnames[bib]
    del bibnames[bib]
    show_collections()

def add_col():
    arg = askstring('', 'name a new collection:')
    if not arg: return
    collections[arg] = []
    show[arg] = True
    show_collections()

def ren_col(col):
    global curbib
    arg = askstring('', 'name a new collection:')
    if not arg: return
    if arg == col: return
    collections[arg] = collections[col]
    del collections[col]
    show[arg] = show[col]
    for bib in list(collections[arg]):
        collections[arg].append(arg+'/'+bib.split('/')[-1])
        collections[arg].remove(bib)
        bibnames[arg+'/'+bib.split('/')[-1]] = bibnames[bib]
        del bibnames[bib]
        if bib == curbib: curbib = collections[arg][-1] # FIXME
    show_collections()
    return

def rem_col(arg):
    global curbib
    print('remove', arg)
    for bibname in collections[arg]:
        collections[''].append('/'+bibname.split('/')[-1])
    for bib in collections[arg]:
        bibnames['/'+bib.split('/')[-1]] = bibnames[bib]
        del bibnames[bib]
        if bib == curbib: curbib = '/'+bib.split('/')[-1]
    del collections[arg]
    show_collections()

def show_bib(bib=''):
    global curbib, area2, scroll2
    if bib:
        curbib = bib
    if not curbib: return
    area2.pack_forget()
    scroll2.pack_forget()
    scroll2 = Scrollbar(area0)
    area2 = Listbox(area0, width=95, yscrollcommand=scroll2.set)
    area2.pack(fill='both', expand=True, side='left')
    scroll2.pack(side='left', fill=Y)
    scroll2.config(command=area2.yview)

    for ref in sorted(bibnames[curbib]):
        text = references[ref][iauthor].replace(' AND ', ' and ').replace(' And ', ' and ' ).split(' and ')[0]
        if references[ref][iyear]:
            text += ' ('+ references[ref][iyear] +') '+ references[ref][ititle]
        else:
            text += ' (n.d.) '+ references[ref][ititle]
        area2.insert(END, texconvert(1, text).replace('{','').replace('}',''))

    def bibselect(event):
        if not event.widget.curselection(): return
        index = int(event.widget.curselection()[0])
        show_ref(sorted(bibnames[curbib])[index])
        for cdx in range(len(collist)):
            if collist[cdx] in bibnames and curref in bibnames[collist[cdx]]:
                area1.itemconfig(cdx, bg='yellow')
            else:
                area1.itemconfig(cdx, bg='')
                if collist[cdx] in collections and not show[collist[cdx]]:
                    for bib in collections[collist[cdx]]:
                        if curref in bibnames[bib]:
                            area1.itemconfig(cdx, bg='yellow')
    def context(event):
        widget = event.widget
        index = widget.nearest(event.y)
        bmenu = Menu(area2, tearoff=0)
        bmenu.add_command(label='add ref', command=add_ref)
        bmenu.post(event.x_root, event.y_root)
        bmenu.grab_set()
        if index < 0: return
        _, yoffset, _, height = widget.bbox(index)
        if event.y > height + yoffset + 5: # XXX 5 is a niceness factor :)
            return # outside of widget.
        if widget['selectmode'] != 'multiple':
            widget.selection_clear(0,'end')
        widget.selection_set(index) # widget.activate(index)
        refs = []
        for idx in event.widget.curselection():
            refs.append(sorted(bibnames[curbib])[idx])
        cpmenu = Menu(bmenu, tearoff=0)
        colmenus = []
        for col in collections:
            if not collections[col]: continue
            colmenus.append(Menu(bmenu, tearoff=0))
            found=False
            for bibliography in collections[col]:
                if len(refs)==1 and refs[0] in bibnames[bibliography]: continue
                colmenus[-1].add_command(label=bibliography.split('/')[-1], command=lambda arg0=refs,arg1=bibliography: copy_ref(arg0, arg1))
                found=True
            if found: cpmenu.add_cascade(label=col, menu=colmenus[-1])
        bmenu.add_cascade(label='copy refs to', menu=cpmenu)    # copy/move ref to other bibliography
        bmenu.add_command(label='remove refs', command=lambda arg=refs: rem_ref(arg))
        rmmenu = Menu(bmenu, tearoff=0)
        rolmenus = []
        for col in collections:
            if not collections[col]: continue
            rolmenus.append(Menu(bmenu, tearoff=0))
            found=False
            for bibliography in collections[col]:
                if len(refs)==1 and refs[0] not in bibnames[bibliography]: continue
                rolmenus[-1].add_command(label=bibliography.split('/')[-1], command=lambda arg0=refs,arg1=bibliography: rem_ref(arg0,arg1))
                found=True
            if found: rmmenu.add_cascade(label=col, menu=rolmenus[-1])
        bmenu.add_cascade(label='remove refs from', menu=rmmenu)
        bmenu.add_command(label='merge sel', command=bmerge)
        bmenu.post(event.x_root, event.y_root)
        bmenu.grab_set()
    area2.bind('<<ListboxSelect>>', bibselect)
    area2.bind('<Button-3>', context)
    set_browse()

def add_bib(collection=''):
    if not collection:
        collection = curbib.split('/')[0]
    res = askstring(collection, 'bibliography name')
    if res == None: return
    collections[collection].append(collection+'/'+res)
    bibnames[collection+'/'+res] = []
    show[collection] = True
    show_collections()

def ren_bib(bib):
    global curbib
    arg = askstring(bib, 'bibliography name')
    if not arg: return
    arg = bib.split('/')[0]+'/'+arg
    if arg == bib: return
    bibnames[arg] = bibnames[bib]
    del bibnames[bib]
    collections[bib.split('/')[0]].remove(bib)
    collections[bib.split('/')[0]].append(arg)
    if bib == curbib: curbib = arg
    show_collections()
    return

def rem_bib(bibname):
    global curbib
    collections[bibname.split('/')[0]].remove(bibname)
    show_collections()
    for ref in bibnames[bibname]:
        found = False
        for col in collections: # collection[bibname] already removed
            for bib in collections[col]:
                if ref in bibnames[bib]:
                    found = True
        if not found and ref in references:
            bibnames['/orphan'].append(ref)
    del bibnames[bibname]
    if bibname == curbib:
        curbib = ''

def activate_fields():
    for idx in range(len(labels)):
        bvalues[idx]['state'] = 'normal'

def valid_file():
    fname = bvalues[ifile].get()
    if fname and not os.path.exists(fname):
        bvalues[ifile]['bg'] = 'yellow'
    else:
        bvalues[ifile]['bg'] = 'white'

def valid_braces(idx):
    if isinstance(bvalues[idx], Entry): val = bvalues[idx].get()
    else:                               val = bvalues[idx].get(0.0,'end')
    nopen  = len(val) - len(val.replace('{',''))
    nclose = len(val) - len(val.replace('}',''))
    if nopen != nclose: bvalues[idx]['bg'] = 'yellow'
    else:               bvalues[idx]['bg'] = 'white'

def show_ref(ref):
    global curref
    if ref != curref and area2['selectmode'] != 'multiple': # clicking on curref will override any changes made; it is intentional
        update_bib(ref)
    curref = ref
    activate_fields()
    bvalues[-1].delete(0, 'end')
    bvalues[-1].insert(0, ref)
    for idx in range(len(labels)):
        if labels[idx] != 'type':
            if isinstance(bvalues[idx], Entry):
                bvalues[idx].delete(0,'end')
            else:
                bvalues[idx].delete(0.0,'end')
            if curref in references:    # it may be deleted
                bvalues[idx].insert(END, texconvert(1, references[ref][idx]) )
            valid_braces(idx)
    valid_file()
    set_type(references[ref][0].lower())
    if not curbib: return
    if curref in bibnames[curbib]:
        idx = sorted(bibnames[curbib]).index(curref)
        area2.selection_set(idx) # restore curref selection
        area2.see(idx)           # restore curref position

def open_file(event):
    fname = bvalues[ifile].get()
    os.system('xdg-open "'+fname+'" &')
def open_doi(event):
    link = bvalues[idoi].get()
    if link[:4] != 'http':
        link = 'http://doi.org/'+link
    os.system('xdg-open "'+link+'" &')

def ren_file(event):
    oldfile = bvalues[ifile].get().replace('file://','')
    ext = oldfile.split('.')[-1]
    path = '/'.join(oldfile.split('/')[:-1])
    author = references[curref][iauthor].split()[0].strip(',')
    year = references[curref][iyear]
    title = references[curref][ititle]
    if not year: year = '-'
    newfile = (path+'/'+(author+' '+year+' '+title).replace('{','').replace('}','').replace(':',''))[:250]+'.'+ext
    os.rename(oldfile, newfile)
    print('->', newfile)
    references[curref][ifile] = newfile #.replace(papersdir,'')
    show_ref(curref)
    return 'break'

def find_doi(fil): #, arg):
    import re
    doi = fil.split('/')[-1].replace('_',' ').replace('-',' ').replace('.',' ').replace(',',' ').strip('01234567890 ').split()[0].lower()
    if re.match('.*[0-9]{4}.*', fil):
        doi += re.sub('.*([0-9]{4}).*', '\\1', fil)
    fileID=open(fil) #.replace('.pdf','.txt'))
    for line in fileID.readlines():
        if re.match('.*doi[^ /]+[: /]([^ ]+).*', line.lower()):
            doi = re.sub('.*doi[^ :/]+[ :/]+([^ ]+).*', '\\1', line)
            break
    fileID.close()
    return doi.strip()

def add_ref(bibname=''):
    if not bibname: bibname=curbib
    res = askstring(bibname, 'enter a key, doi, file or url')
    if res == None: return
    if not res: res = valid_key('unnamed')
    fil = ''
    if '.pdf' in res.lower() and os.path.exists(res.replace('file://','')):
        fil = res.replace('file://','')
        os.system('pdftotext "'+fil+'" "/tmp/'+res.split('/')[-1].replace('.pdf','.txt')+'"') #/tmp/ref.tmp')
    elif res[:4]=='http':   # FIXME: it is broken
        fil = res
        os.system('curl '+res+'> /tmp/ref.tmp')
    if fil:
        res = find_doi('/tmp/'+res.split('/')[-1].replace('.pdf','.txt'))
    if '/' in res:  # probably a DOI
        found = False
        for ref in references:
            if ref == references[ref][idoi]:
                print('found', ref)
                found = True
                break
        if not found:
            ref, data = parse_doi(res)
            references[ref] = data
    else:
        ref = valid_key(res)
        references[ref] = list(blank)
        references[ref][itype] = 'article'
    if fil: references[ref][ifile] = fil #.replace(papersdir,'')
    if ref not in bibnames[bibname]:
        bibnames[bibname].append(ref)
    show_bib(bibname)
    show_ref(ref)

def parse_ref_doi(doi):
    update()
    ref, data = parse_doi(bvalues[idoi].get())
    for idx in range(1,len(labels)):    # don't need to search for 'type'
        if not references[curref][idx]:
            references[curref][idx] = data[idx]
    show_ref(curref)

def parse_doi(doi):
    tmpdata = list(blank)
#   example output = ' @article{2002, title={Selective anticancer drugs}, volume={1}, ISSN={1474-1784}, url={http://dx.doi.org/10.1038/nrd842}, DOI={10.1038/nrd842}, number={7}, journal={Nature Reviews Drug Discovery}, publisher={Springer Science and Business Media LLC}, author={Atkins, Joshua H. and Gershell, Leland J.}, year={2002}, month={Jul}, pages={491–492} }'#.strip('}').strip()
    p = os.popen('curl -LH "Accept: text/bibliography; style=bibtex" "https://doi.org/'+doi+'"')
    output = p.read()
    ldx=0
    for line in [output.split(',')[0]]+','.join(output.split(',')[1:]).strip('} \n').split('},'):
            ldx+=1
            if line and line.strip()[0] == '@':
                btype = line.split('{')[0].strip(' @')
                tmpdata[itype] = btype
            line+='}'
            print(ldx, line)
            for idx in range(1,len(labels)):    # don't need to search for 'type'
                if labels[idx]+'=' in line.lower() or labels[idx]+' =' in line.lower():
                    tmpdata[idx] = line.split('=')[-1].strip(' ,\n')    # [1:-1]
                    if tmpdata[idx][0]=='{' and tmpdata[idx][-1]=='}':
                        tmpdata[idx] = tmpdata[idx][1:-1]   # strip surrounding braces or quotes
    ref = valid_key(tmpdata[iauthor].split()[0].strip('.,-').lower()+tmpdata[iyear].strip('{}"'))
    return ref, tmpdata

def get_abstract():
    doi=bvalues[idoi].get() #'10.1109/TASC.2010.2088091'
    p = os.popen('curl -L "https://doi.org/'+doi+'"')
    output = p.read()
    inabs=False
    ablines=[]
    for line in output.split('\n'):
        if 'og:description' in line:
            inabs=True
        if inabs: ablines.append(line.strip())
        if '/>' in line: inabs=False
    if ablines:
        references[curref][iabstract] = ' '.join(ablines)
        show_ref(curref)
    return 'break'

def update_bib(ref=''):
    global curref
    if update():
        if ref: curref=ref
        show_bib()
    return 'break'

def update():
    global curref
    if not curref or curref not in references: return   # deleted key
    newkey = bvalues[-1].get()
    refresh = False
    if newkey != curref:
        refresh = True
        newkey = valid_key(newkey)
        references[newkey] = references[curref]
        del references[curref]
        for bib in bibnames:
            if curref in bibnames[bib]:
                bibnames[bib].remove(curref)
                bibnames[bib].append(newkey)
        curref = newkey
    for k in references[curref][ikeywords].replace(';',',').split(','):
        k = k.lower().strip()
        if k in keywords:
            keywords[k] -= 1
            if not keywords[k]:
                del keywords[k]
    for idx in range(len(labels)):
        if labels[idx] == 'type':
            val = bvalues[idx]['text']
        else:
            if isinstance(bvalues[idx], Entry):
                val = bvalues[idx].get()
            else:
                val = bvalues[idx].get(0.0, 'end').strip()
            if idx != ifile:
                val = texconvert(0, val)
        if (idx==ititle or idx==iyear or idx==iauthor) and references[curref][idx] != val: #.replace('\n',' '):
            refresh = True
        references[curref][idx] = val.replace('\n',' ')
    for k in references[curref][ikeywords].replace(';',',').split(','):
        k = k.lower().strip()
        if k not in keywords:
            keywords[k] = 0
        keywords[k] += 1
    set_kmenu()
    return refresh

def save_bibs(bib='', bibfile='', short=False):
    update()
    if userbibfile: bibfile=userbibfile
    if not bibfile:
        fileID = open(basedir+'/collections.dat', 'w')
        for col in sorted(collections):
            if col:
                fileID.write('# '+col+'\n')
            for bib in sorted(collections[col]):
                fileID.write(bib.split('/')[-1]+'\t'+' '.join(bibnames[bib])+'\n')
            fileID.write('\n')
        fileID.close()
        bibfile = basedir+'/references.bib'
        refs = list(references)
        nfields = len(labels)
    else:
        if not bib: bib=curbib
        refs = bibnames[bib]
        nfields = idoi+1
    fileID = open(bibfile, 'w')
    for ref in sorted(refs):
        fileID.write('@'+references[ref][itype]+'{'+ref)
        for idx in range(1,nfields):
            if not references[ref][idx]: continue
            if short and idx==ijournal and bibfile:
                fileID.write(',\n\t'+labels[idx]+' = {'+journal_abbrev(references[ref][idx])+'}')
            else:
                fileID.write(',\n\t'+labels[idx]+' = {'+references[ref][idx]+'}')
        fileID.write('\n}\n\n')
    fileID.close()

def format_string(text):
    res = []
    inbrace = False
    for s in text.strip().split():
        if s[0] == '{': inbrace=True
        if inbrace:       res.append(s)
        elif len(s) <= 3: res.append(s.lower())
        else:             res.append(s.title())
        if s[0] == '}': inbrace=False
    text = ' '.join(res)
    return text[0].upper()+text[1:]

def format_title(idx):
    if isinstance(bvalues[idx], Entry):
        text = format_string(bvalues[idx].get())
        bvalues[idx].delete(0,'end')
        bvalues[idx].insert(0, text)
    else:
        text = format_string(bvalues[idx].get(0.0,'end')) # .capitalize()
        bvalues[idx].delete(0.0,'end')
        bvalues[idx].insert(0.0, text)
    return 'break'  # prevent the default action

def format_key(event):
    text = bvalues[ikey].get()
    if text == curref: return
    bvalues[ikey].delete(0,'end')
    bvalues[ikey].insert(0, valid_key(text))

def copy_ref(refs, to):
    for ref in refs:
        if ref not in bibnames[to]:
            bibnames[to].append(ref)
    show_bib()

def rem_ref(refs, bib=''):
    if not bib: bib=curbib
    for ref in refs:
        if ref in bibnames[bib]:
            bibnames[bib].remove(ref)
        if curbib == '/orphan':
            del references[ref]
        else:
            add_orphan(ref)
    if bib==curbib:
        show_bib()

def write_fmtrefs(sty, mk='html'):
    if not curbib: return
    filetypes = [('html','.html')]
    for fname in glob.glob(basedir+'/*.mk'):
        flabel = fname.replace(basedir,'').strip('/').split('.')[0]
        if flabel!='html':
            filetypes.append((flabel, '.'+flabel))
    outfile = asksaveasfilename(defaultextension='.html', filetypes=filetypes)
    if not outfile: return
    if '.' in outfile:
      if outfile.split('.')[-1] in [ext[0] for ext in filetypes]:
        mk = outfile.split('.')[-1]
    fileID = open(outfile, 'w')
    for line in out_fmtrefs(sty, mk, bibnames[curbib]):
        if line:
            fileID.write(line+'\n')
    fileID.close()

def app_quit():
    print('save and exit')
    save_bibs()
    app.quit()

for arg in list(sys.argv[1:]):
    if os.path.exists(arg) or arg[-4:]=='.bib':
        userbibfile = arg
        collections['']=[]
        read_bibfile(arg)
        sys.argv.remove(arg)

if not collections:
    read_collections()
    read_bibfile()

app = Tk()
do_gui()
if not curbib:
    area2.insert(END, 'getting keywords...')
get_keywords()
set_kmenu()
if not curbib:
    area2.delete(END)
    area2.insert(END, 'searching for orphan references...')
set_orphan()
if not curbib:
    area2.delete(END)
    area2.insert(END, 'left list:')
    area2.insert(END, '    <B1> open collections / select bibliography')
    area2.insert(END, '    <B3> context menu')
    area2.insert(END, 'right inspector:')
    area2.insert(END, '    <Return> stores data into reference')
    area2.insert(END, '    <C-Return> format title (text entries)')
    area2.insert(END, '    <C-Return> retrieve data (doi entry)')
    area2.insert(END, '    <C-Return> rename file (file entry)')
    area2.insert(END, '    <B3> open DOI/file')
    area2.insert(END, '    <C-B1> move file')
app.mainloop()

