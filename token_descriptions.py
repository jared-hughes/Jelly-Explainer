import os, re

# This takes the quicks.md and atoms.md in jelly.wiki, parses them, and saves the output to wikis.py

files = []
cur_path = os.path.dirname(__file__)
for file_name in ["Atoms.md","Quicks.md"]:
    new_path = os.path.relpath("jelly.wiki/"+file_name,cur_path)
    with open(new_path, 'r') as f:
        files.append(f.read())

atoms_wiki = files[0]
quicks_wiki = files[1]

def to_ascii(html):
    html = html.replace("**","").replace("&minus;","-")
    html = re.sub(r"\[(.*?)\]\(.*?\)",r"\1",html)
    html = re.sub(r"<sup>(.*)</sup>",r"-\1",html)
    return html

def to_dict(wiki):
    atoms = dict(re.findall(r'` *(..?) *` *\| *([^\|\n]*)', wiki))
    return {k:atoms[k].replace("`","") for k in atoms}

def to_tail(wiki):
    atoms = dict([(k[0],k[2]) for k in re.findall(r'` *(..?) *` *\| *([^\|\n]*)\| *([^\|\n]*)', wiki)])
    return {k:atoms[k].replace("`","") for k in atoms}

atoms_wiki = to_ascii(atoms_wiki)
quicks_wiki = to_ascii(quicks_wiki)

atoms = to_dict(atoms_wiki)
quicks = to_dict(quicks_wiki)
quicks_tail = to_tail(quicks_wiki)

with open('wikis.py', 'w') as f:
    f.write("#-*- encoding: utf-8 -*-\n")

with open('wikis.py', 'a') as f:
    f.write("\natoms_wiki="+repr(atoms))
    f.write("\nquicks_wiki="+repr(quicks))
    f.write("\nquicks_tail="+repr(quicks_tail))
