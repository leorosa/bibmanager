#! /usr/bin/python3

# https://www.bibtex.com/e/entry-types/
labels = [ 'type', 'title', 'author', 'booktitle', 'journal', 'publisher', 'howpublished', 'organization', 'institution', 'address', 'editor', 'year', 'month', 'volume', 'number', 'series', 'pages', 'school', 'issn', 'doi', 'file', 'keywords', 'abstract', 'note' ]
itype       = labels.index('type')
iauthor     = labels.index('author')
iyear       = labels.index('year')

blank  = ['']*len(labels)
unknown= ['?']*len(labels)
citstyle = 'authoryear'

import os, glob, sys
from jabbrev import journal_abbrev
from texconvert import texconvert

basedir = os.environ['HOME']+'/.local/share/bibmanager'
userbibfile = ''
bibnames = {}       # bibfiles
references = {}     # citations

def read_bibfile(bibfile=''):
    add = False
    if not bibfile:
        bibfile = basedir+'/references.bib'
        bibname = ''
    else:
        bibname = '/'.join( [colname, bibfile.split('/')[-1]] )
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

def read_style(sty):
    global refshort, reford, refdir, refnam, citstyle
    style = {}
    refshort = False
    reford = False
    refdir = False
    refnam = False
    if os.path.isfile(basedir+'/'+sty+'.sty'):
        sty = basedir+'/'+sty+'.sty'
    if not os.path.isfile(sty):
        print(sty, 'not found')
        exit()
    fileID = open(sty)
    for line in fileID.readlines():
        line = line.strip('\n')
        if not line: continue
        elif '	' not in line:
            if line.strip()=='short':
                refshort = True
            elif line.strip()[:7]=='ordered':
                reford = True
                if len(line.strip())>7:
                    reford = line.strip()[7:]
            elif line.strip()=='reverse':
                refdir = True
            elif line.strip()=='namesfirst':
                refnam = True
            elif line.strip()[:3]=='cit':
                citstyle = line.strip()[3:]
            elif line.strip()[0]=='#':
                label = line.strip(' #')
                style[label] = {}
            elif line in style:
                for key in style[line]:
                    style[label][key] = style[line][key]
        else:
            style[label][line.split('	')[0]] = line.split('	')[1:]
    fileID.close()
    if usercitstyle: citstyle=usercitstyle
    return style

def read_markup(mk):
    markup = {}
    if os.path.isfile(basedir+'/'+mk+'.mk'):
        mk = basedir+'/'+mk+'.mk'
    if not os.path.isfile(mk):
        print(mk, 'not found')
        exit()
    with open(mk) as fileID:
        for line in fileID.readlines():
            markup[line.split('	')[0]] = line.strip('\n').split('	')[1:]
    return markup

def out_fmtrefs(sty, mk, keys):
    markup = read_markup(mk)
    style = read_style(sty)
    if citstyle=='authoryear': lst = markup['ulst']
    else:      lst = markup['olst']
    lines = []
    lines.append(markup['body'][0])
    lines.append(lst[0])
    lidx = 0
    for ref in keys:
        if ref not in references: references[ref]=unknown
    if reford in labels:
        ridx = labels.index(reford)
        keys = sorted(keys, key=lambda item: references[item][ridx], reverse=refdir)
    elif reford: keys = sorted(keys, reverse=refdir)

    ridx=0
    for ref in keys:
        ridx+=1
        reftype = references[ref][itype]
        if etype and reftype not in etype: continue
        if reftype not in style: reftype = 'default'
        refline = ''
        for field in style[reftype]:
            idx = labels.index(field)
            sfield = references[ref][idx]
            if field=='author':
                authors = []
                for author in get_authors(sfield):
                    authors.append(author)
                sfield = ', '.join(authors)
            sfield = texconvert(1, sfield).replace('{','').replace('}','')
            if not sfield: continue
            if 'upper' in style[reftype][field][0].split(','): sfield = sfield.upper()
            sfield = style[reftype][field][1]+sfield+style[reftype][field][2] # pre/pos
            if refshort and field=='journal': sfield = journal_abbrev(sfield)
            if 'bold' in style[reftype][field][0].split(','): sfield = markup['bold'][0] + sfield + markup['bold'][-1]
            if 'ital' in style[reftype][field][0].split(','): sfield = markup['ital'][0] + sfield + markup['ital'][-1]
            if 'ital' in style[reftype][field][0].split(','): sfield = markup['undr'][0] + sfield + markup['undr'][-1]
            refline += sfield+' '
        if refline:
            lines.append(lst[1].replace('%d',str(ridx))+' '+refline)
    lines.append(lst[-1])
    lines.append(markup['body'][-1])
    return lines

def get_authors(sfield):
    authors = []
    for author in sfield.replace(' AND ', ' and ').replace(' And ', ' and ' ).split(' and '):
        prename = ''
        if ',' in author:
            prename = author.split(',')[-1].strip()
            surname = author.split(',')[0].strip()
        elif ' ' in author:
            prename = ' '.join(author.replace(' ',' ').split(' ')[:-1]).strip()
            surname = author.replace(' ',' ').split(' ')[-1].strip()
        if prename:
            if refshort:
                prename = ' '.join([n[0]+'.' for n in prename.split()])
            if refnam: author = prename+' '+surname
            else:      author = surname+', '+prename
        authors.append(author)
    return authors

def print_fmtrefs(sty, mk, keys):
    for line in out_fmtrefs(sty, mk, keys):
        if line:
            print(line)
    return

for arg in list(sys.argv[1:]):
    if os.path.exists(arg) or arg[-4:]=='.bib':
        userbibfile = arg
        sys.argv.remove(arg)

read_bibfile()

mk='html'; sty='short'; keys=''; etype=''; ckeys=''; usercitstyle=''
read_style(sty)     # define refshort needed for get_authors()
for arg in sys.argv[1:]:
    if arg.split('=')[0]=='-markup':
        if '=' not in arg:
            print(mk, [f.split('/')[-1].split('.')[0] for f in glob.glob(basedir+'/*.mk')])
            exit()
        mk=arg.split('=')[1]
    elif arg.split('=')[0]=='-style':
        if '=' not in arg:
            print(sty, [f.split('/')[-1].split('.')[0] for f in glob.glob(basedir+'/*.sty')])
            exit()
        sty = arg.split('=')[1]
        read_style(sty)
    elif arg.split('=')[0]=='-citstyle':
        if '=' not in arg:
            print(citstyle)
            exit()
        usercitstyle=arg.split('=')[1].split(',')
    elif arg.split('=')[0]=='-keys':
        keys=arg.split('=')[1].split(',')
    elif arg.split('=')[0]=='-cite':
        ckeys=arg.split('=')[1].split(',')
    elif arg.split('=')[0]=='-type':
        etype=arg.split('=')[1].split(',')
    elif arg=='-help':
        print(sys.argv[0], '[bibfile] [colname] [-markup=markup] [-style=sty] [-citstyle=authoryear|number|super] [-cite=keys] [-keys=keys] [-type=type] [-list/-help]')
        exit()
    elif arg in bibnames: curbib=arg
    else:
        for bib in bibnames: print(bib)
        if arg!='-list':
            print(arg, 'unknown')
        exit()

if userbibfile or keys:
    if not keys:
        keys = bibnames['']
    print_fmtrefs(sty, mk, keys)
elif ckeys: # output as 'authoryear'; citstyle is to be applied in text processor
    for key in ckeys:
        if key not in references: print('@'+key); continue
        authors = get_authors(references[key][iauthor])
        author = authors[0].split(',')[0]
        if   len(authors)>2: author += ' et al.'
        elif len(authors)==2:
            author += ' and '+authors[1].split(',')[0]
        print(author+' ('+references[key][iyear]+')')
