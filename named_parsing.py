#!/usr/bin/env python3
#-*- encoding:utf-8 -*-
from jelly import *

# NOTE: This still has indentation issues

from wikis import quicks_wiki, atoms_wiki, quicks_tail
#quicks_tail to be used to format quicks like so:
#  Ternary if
#    <condition>
#     ...
#   <if-clause>
#     ...
#   <else-clause>
#     ...

for k in quicks:
	quicks[k].token = k
for k in hypers:
	hypers[k].token = k
for k in atoms:
	atoms[k].token = k

def is_litlist(literal):
	return re.match(str_litlist+"$",literal)!=None and re.match(str_literal+"$",literal)==None

def literal_type(literal):
	out = ""
	lit = literal
	if lit[0] == "“":
		if '“' in lit[1:]:
			out = ["list"," of %ss "]
		else:
			out = ["%s"]
		if lit[-1] == '”':
			out[-1] = out[-1]%["string"]
		elif lit[-1] == '»':
			out[-1] = out[-1]%['dictionary-compressed string']
		elif lit[-1] == '‘':
			out[-1] = out[-1]%['code-page index list']
		elif lit[-1] == '’':
			out[-1] = out[-1]%['literal']
	elif lit[0] == '⁽':
		out = ["integer"]
	elif lit[0] == '⁾':
		out = ["2-char string"]
	elif lit[0] == '”':
		out = ["char"]
	else:
		out = ["integer"]
	return out


def literal_title(literal):
	if is_litlist(literal):
		equiv = "[" + ','.join(map(mono_literal_equivalent,literal.split(","))) + "]"
		name = map(literal_type,literal.split(","))
		for k in name:
			first = k
			break
		if all(item == first for item in name):
			first.insert(1,"s")
			name = "list of "+ ''.join(first)
		else:
			name = "list"
	else:
		equiv = mono_literal_equivalent(literal)
		name = ''.join(literal_type(literal))

	return "The literal "+name+" "+equiv

def mono_literal_equivalent(mono_literal):
	evaled = jelly_eval(mono_literal,[])
	if type(evaled) == list:
		if type(evaled[0]) == list:
			if type(evaled[0][0]) == str:
				evaled = [''.join(k) for k in evaled]
		elif type(evaled[0]) == str:
			evaled = ''.join(evaled)
	if type(evaled) == str:
		evaled = "'" + evaled + "'"
	return str(evaled)

def chainsep_title(token):
	assert token in chain_separators.keys()
	value = chain_separators[token]
	return "Start a new "+['nil','mon','dy'][value[0]]+"adic chain"+(" with reversed arguments" if not value[1] else "")

def name(token):
	if len(token) == 0:
		return ""
	elif token in atoms_wiki:
		return atoms_wiki[token]
	elif token in quicks_wiki:
		return quicks_wiki[token]
	elif token in str_arities:
		return chainsep_title(token)
	else:
		return literal_title(token)

def token_attrdict(ls):
	assert type(ls) in [str,list,attrdict]
	if type(ls) == str:
		if ls in quicks:
			return quicks[ls]
		elif ls in atoms:
			return atoms[ls]
		elif ls in hypers:
			return hypers[ls]
		else:
			return create_literal(regex_liter.sub(parse_literal, ls))
	elif type(ls) == list:
		return [token_attrdict(k) for k in ls]
	elif type(ls) == attrdict:
		return token_attrdict(ls.token)

def indent_deepest(ls):
	if type(ls) == list:
		return [indent_deepest(k) for k in ls]
	ls.indentation += 2
	return ls

# structure derived from Jelly's parse_code() function.
regex_token_sep = re.compile(str_nonlits + "|" + str_litlist + "|[" + str_arities +"]|")
def parse_code_named(code):
	lines_match = regex_flink.finditer(code)
	lines = list(lines_match)
	lines_str = [line.group(0) for line in lines]
	lines_match = regex_flink.finditer(code)
	links = [[] for line in lines]
	for index, line_match in enumerate(lines_match):
		line = line_match.group(0)
		chains = links[index]
		for word_match in regex_chain.finditer(line):
			word = word_match.group(0)
			chain = []
			for match in regex_token_sep.finditer(word):
				token = match.group(0)
				token_span = attrdict(token=token, span=match.span(), word_start=word_match.start(), line_len = len(line), name=name(token), indentation=0)
				if not len(token):
					break;
				if token in atoms:
					chain.append(token_span)
				elif token in quicks:
					popped = []
					while not quicks[token].condition([token_attrdict(k) for k in popped]) and (chain or chains):
						popped.insert(0, chain.pop() if chain else chains.pop())
					popped = indent_deepest(popped)
					#token_span = indent_deepest(token_span)
					chain.append([popped, token_span])
				elif token in hypers:
					chain.append(token_span)
				else:
					chain.append(token_span)
			chains.append(chain)
	return (links, lines_str)


def order(tokens):
	if type(tokens) in (list,tuple):
		# system to order more naturally e.g. ABC? -> ?CAB [if C then A else B].
		# Improve based on quick? Future difficulty: "/" could have two definitions
		if len(tokens)==0:
			return []
		if len(tokens)==1:
			return [order(tokens[~0])]
		if len(tokens)==2:
			return [order(tokens[~0]),order(tokens[~1])]
		if len(tokens)==3:
			return [order(tokens[~0]),order(tokens[~2]),order(tokens[~1])]
	elif type(tokens) == attrdict:
		return tokens
	else:
		return tokens

def order_ranking(ranking):
	out = []
	for link in ranking:
		p = []
		for chain in link:
			o = []
			for token_seq in chain:
				ordered = order(token_seq)
				if type(ordered) == attrdict:
					o.append(ordered)
				else:
					for k in order(token_seq):
						o.append(k)
			p.append(o)
		out.append(p)
	return out

def explain_token(token):
	assert type(token) in [str, list, tuple, attrdict]
	if type(token) == str:
		return [token, name(token)]
	elif type(token) == attrdict:
		return token
	elif type(token) in [list, tuple]:
		o = []
		for tok in token:
			e = explain_token(tok)
			o+=[e]
		return o

def filter_out(ls, element):
	if type(ls) == list:
		return [filter_out(k, element) for k in ls if k!=element]
	else:
		return ls

def form_neat(ranking):
	if type(ranking) == attrdict:
		return "name: "+ranking.name
	else:
		return [form_neat(k) for k in ranking]

def explain(code):
	ranking, lines = parse_code_named(code)
	print("RANKING: ",ranking)
	ranking = filter_out(ranking, [])
	ranking = order_ranking(ranking)
	print("RANKING: ",ranking)
	explanation = []
	# Iteration form not pythonic but necessary to append lines from parse_code_named. Maybe interleave instead?
	for line_num in range(len(ranking)):
		line = ranking[line_num]
		explanation.append(lines[line_num])
		for chain in line:
			explanation.append(explain_token(chain))
	return render(explanation)

def render(ordered,join="\n\n"):
	assert type(ordered) in [str, list, attrdict]
	if type(ordered) == list:
		# this looks and is horrible. TODO:Change
		lines = ["\n".join(   [a for a in render(k,"\n").split("\n")]   ) for k in ordered]
		o = join.join(lines)
		return re.sub(r"(\n\n[^\n]+\n)\n",r"\1",o)
	elif type(ordered) == str:
		return ordered
	elif type(ordered) == attrdict:
		start = ordered.span[0]+ordered.word_start
		return " "*(start)+ordered.token+" "*(ordered.line_len-start-len(ordered.token))+" "*ordered.indentation+"    "+ordered.name

test_string = """3,µ+5µ7C
01P?2S?+3
5Ç+5©
P01?
3
1+2+3+4+5
1+2µ3+45
CN$
+5/
+/
SƤ
S€"""

print(explain(test_string))
k = attrdict(a=5, b=3, c=1)
