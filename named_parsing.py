import jelly
from jelly import *

from wikis import quicks_wiki, atoms_wiki, quicks_tail

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

def name(token):
	if token in atoms_wiki:
		return atoms_wiki[token]
	elif token in quicks_wiki:
		return quicks_wiki[token]
	else:
		return literal_title(token)

def token_attrdict(ls):
	assert type(ls) in [str,list]
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


# structure derived from Jelly's parse_code() function.
def parse_code_named2(code):
	lines = regex_flink.findall(code)
	links = [[] for line in lines]
	for index, line in enumerate(lines):
		chains = links[index]
		for word in regex_chain.findall(line):
			chain = []
			arity, isForward = chain_separators.get(word[0], default_chain_separation)
			for token in regex_token.findall(word):
				if token in atoms:
					chain.append(token)
				elif token in quicks:
					popped = []
					while not quicks[token].condition([token_attrdict(k) for k in popped]) and (chain or chains):
						popped.insert(0, chain.pop() if chain else chains.pop())
						#print(popped)
					chain.append([popped, token])
				elif token in hypers:
					x = chain.pop() if chain else chains.pop()
					chain.append(token)
				else:
					chain.append(token)
			chains.append(chain)
	return (links, lines)

def order(tokens):
	if type(tokens) in (list,tuple):
		if len(tokens)==0:
			return []
		if len(tokens)==1:
			return [order(tokens[~0])]
		if len(tokens)==2:
			return [order(tokens[~0]),order(tokens[~1])]
		if len(tokens)==3:
			return [order(tokens[~0]),order(tokens[~2]),order(tokens[~1])]
	else:
		return tokens

def order_ranking(ranking):
	out = []
	for link in ranking:
		p = []
		for chain in link:
			o = []
			for token_seq in chain:
				for k in order(token_seq):
					o.append(k)
				#o.append(order(token_seq))
				#o.append(token_seq)
			p.append(o)
		out.append(p)
	return out

def explain_token(token):
	assert type(token) in [str, list, tuple]
	if type(token) == str:
		#if token in quicks
		return [name(token)]
	elif type(token) in [list, tuple]:
		o = []
		for tok in token:
			e = explain_token(tok)
			o+=[e]
		return o


def explain(code):
	ranking, lines = parse_code_named2(code)
	lines.reverse()
	ranking = order_ranking(ranking)
	#out = flatten(out)
	explanation = []
	for line in ranking:
		for chain in line:
			explanation.append(explain_token(chain))
	print(explanation)
	renders = []

	return render(explanation)

	return explanation
	return ranking

# render(k) => newline-separated lines.
def render(ordered):
	assert type(ordered) in [str, list, tuple]
	if type(ordered) in [list, tuple]:
		return '\n'.join(["\n".join(["  "+a for a in render(k).split("\n")]) for k in ordered])
	if type(ordered) == str:
		return ordered

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


print(order_ranking(parse_code_named2(test_string)[0]))
print(explain(test_string))
