#! /usr/bin/python3

# 2026-07-08  use os.environ['HOME']
# 2024-05-23  print messages in stderr
# 2022-07-16  changed logic in order to parse standard input and any file given
# 2022-07-10  fixed 'short-' lookup
# 2022-06-06  initial version
#             can abbreviate a given string
#             can read a bibfile and abbreviate journal names

import os, sys, glob

wtable = {}
source = glob.glob(os.environ['HOME']+'/.local/share/bibmanager/ltwa_*.csv')
basedir = os.environ['HOME']+'.local/bibmanager'
if not source:
    sys.stderr.write('no abbreviation file found; download one in https://www.issn.org/services/online-services/access-to-the-ltwa/\n')
    exit()

def read_abbrev(fname):
    sys.stderr.write('abbrev. file: %s\n' % fname)
    fileID = open(source[0], 'r')
    for line in fileID.readlines():
        line = line.replace('"','')
        key = line.split(';')[0].lower()
        val = line.split(';')[1]
        if val.lower() == 'n.a.':
            val = key
        wtable[key] = val

def word_abbrev(word):
    key = word.lower()
    if key in wtable:
        return wtable[key].title()
#   for idx in range(0,len(key)-1):
#       if key[:-idx]+'-' in wtable:
#           return wtable[key[:-idx]+'-'].title()
    while key:
        if key+'-' in wtable:
            return wtable[key+'-'].title()
        key = key[:-1]
    return ''

def journal_abbrev(title):
    stitle = []
    for word in title.split():
        stitle.append(word_abbrev(word))
    return ' '.join([ key for key in stitle if key != '' ])

def file_abbrev(fname):
    fileID = open(fname)
    for line in fileID.readlines():
        if fname[-4:].lower() != '.bib':
            print(journal_abbrev(line))
        elif 'journal = ' in line.lower() and '.' not in line:
            journal = line.split('=')[1].strip(' "{},\n')
            print('	journal = {' + journal_abbrev(journal) + '},' )
        else:
            print(line.rstrip())
    print(fname)
    return

read_abbrev(source[0])

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        file_abbrev(sys.argv[1])
    else:
      while True:
        try: print(journal_abbrev( input('') ) )
        except: exit()
