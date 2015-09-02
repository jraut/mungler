# -*- coding: utf-8 -*-
import re, os, sys, pickle

class TextParser:
	soft = False
	def __init__(self, ignore = []):
		self.ignore = ignore
		for f in self.sortments: 
			self.re_compiled[f] = re.compile(self.re_patterns[f])

	re_compiled = {}
	re_patterns = {
	'console': r"(?xms)(?P<console>^\s*console\..*?$)",
	'comment': r"(?xms)(?P<comment>(\/\*.*?\*\/)|(\/\/.*?$))",
	'empty_line': r"^\s*?$",
	'whitespace': r"\s\s*",
	'txt':  r"""(?xms)
			(?P<string_opening>["'])
			(?P<string>.*?)
			(?P=string_opening)
			""",

	'brackets': r"(?xms)\{(?P<brackets>[^}]*? (\{[^}]*?\})*? [^}]+? )\}",
	'parenthesis': r"(?xms)\((?P<parenthesis> ([(][^)]*?[)])*? [^)]+? )\)",
	
	#remove hyphen if substractions are without spaces in your code	
	'identifier': r"(?<!\/)\b(?P<identifier>[a-zA-Z][\w-]*)\b",
	
	'phtml': r"""(?xms)

			(?<=id=")\b(?P<idName>\w+?)(?=") |			
			(?<=class=")(?P<className>[^"]*?)(?=") |
			(?<=%-)\s*(?P<identifier>[^%]+?)\s*(?=%>)
			""",

	'css': r"""(?xms)
			(?P<properties>\{[^}]*?\}) |
			(?<=\#)(?P<idName>\w+)\b |			
			(?<=\.)(?P<className>\w+)\b
		""",
	}
	re_patterns['php'] = re_patterns['txt']
	re_patterns['html'] = re_patterns['phtml']
	re_patterns['js'] = "|".join([re_patterns['txt'], 
			re_patterns['brackets'], 
			re_patterns['parenthesis'], 
			re_patterns['identifier']])

	
	def parse(self, filetype, content):
		if filetype in self.sortments:
			def f(match):

				return self.sortments[filetype](self, match)
			return self.re_compiled[filetype].sub(f, content)
		
	def remove_console_rows(self, t):
		return re.sub(self.re_patterns['console'], "", t)

	def remove_comments(self, t):
		return re.sub(self.re_patterns['comment'], "", t)

	def remove_empty_lines(self, t):
		return re.sub(self.re_patterns['empty_line'], "", t)

	def _nom_update(self, t):
		if t in self.nominator.nominations:
			return self.nominator.nominations[t] 
		else:
			return self.nominator.add(t)

	def _nom_find(self, t):
		if t in self.nominator.nominations:
			return self.nominator.nominations[t] 
		else:
			return t
		

	def mungle_identifier(self, t, soft=None):
		if soft is None:
			soft = self.soft
		if t in self.ignore:
			return t
		if soft:
			return self._nom_find(t)
		else:
			return self._nom_update(t)

	def phtml(self, match):
		matchgroups = match.groupdict()
		for g, c in matchgroups.iteritems():
			if c is not None:
				if g == 'className':
					return " ".join([
						self.mungle_identifier(n) for n in c.split(" ")])
				else:
					return self.mungle_identifier(c)

	def php(self, match):
		matchdict = match.groupdict()
		for g, c in matchdict.iteritems():
			if c is not None:
				if g in ('string'):
					return (match.group('string_opening') +
							self.mungle_identifier(c, True) +
							match.group('string_opening'))

	def css(self, match):
		matchdict = match.groupdict()
		for g, c in matchdict.iteritems():
			if c is not None:
				if g == "properties":
					return c
				elif g in ('idName', 'className'):
					return self.mungle_identifier(c)
				else:
					return c

	def js(self, match):
		matchdict = match.groupdict()
		for g, c in matchdict.iteritems():
			#print g, c, match.groups()
			if c is not None:
				if g in ('string_opening', 'string'):
					return (match.group('string_opening') +
							self.parse('js', match.group('string')) +
							match.group('string_opening'))
				elif g == 'brackets':
					return '{'+ self.parse('js', c) + '}'
				elif g == 'parenthesis':
					return '('+ self.parse('js', c) + ')'
				elif g == 'identifier':
					return self.mungle_identifier(c)
				else:
					# this sould not be reached
					return self.parse('js', c)
	
	sortments = {
		'phtml': phtml,
		'html': phtml,
		'php': php,
		'js': js,
		'css': css
	}	 

class Nominator:
	nominations = {}
	i = 0
	def __init__(self, ignore = []):
		self.ignore = ignore
	
	charmap = tuple([chr(i) for i in range(ord('a'), ord('z')+1)])

	def int_to_charseq(self, int_target):
		charseq = ""
		base_n = len(self.charmap)
		seq_length = 1
		# max_num_expressed = seq_length ** base_n 
		while base_n ** seq_length < int_target:
			seq_length += 1
		seq_i = range(0, seq_length)
		seq_i.reverse()
		for e in seq_i:
			max_num_expressed = base_n ** e
			n = int_target / max_num_expressed
			int_target %= max_num_expressed
			charseq += self.charmap[n-1]
		return charseq
	
	def next(self):
		charseq = self.int_to_charseq(self.i)
		self.i += 1
		return charseq

	def add(self, t):
		charseq = self.next()
		while charseq in self.ignore:
			charseq = self.next()
		self.nominations[t] = charseq
		return self.nominations[t]

def import_nominations(filename):
	nominations_map = {}
	if os.path.isfile(filename):
			text = open(filename, 'r').read()
	if (text):
		a = re.compile(r"""
			^(\w+):\s*(\w+)$""", re.M)
		for match in a.finditer(text):
			nominations_map[match.group(1)] = match.group(2)
	return nominations_map

# Imports a plaintext file 
def import_reserved(filename):
	array = []
	if os.path.isfile(filename):
			text = open(filename, 'r').read()
	if (text):
		a = re.compile(r"""(?xms)
			(?P<string_opening>["'])
			(?P<string>.*?)
			(?P=string_opening)
			""")
		array = [i.group('string') for i in a.finditer(text)]
	return array

RESERVED_WORDS = [

]
	
def search_for_files(
		dir, skipped=['vendor', 'mungled'], 
		recursive=True, filetypes=['js','css','html','phtml']): 
	paths_arr = []
	dirlist = os.listdir(dir)
	for t in dirlist:
		t_pointer = dir + '/' + t
		if t not in skipped and t_pointer not in skipped:
			if os.path.isdir(t_pointer) and recursive:
				paths_arr.extend( search_for_files(t_pointer, 
					skipped, recursive, 
					filetypes))
			elif os.path.isfile(t_pointer):
				if (len(t.split(".")) > 1 and 
					t.split(".")[-1] in filetypes):
					paths_arr.append(t_pointer)
	return paths_arr	
	
def file_export(
			filename, dir="mungled", 
			basedir=os.path.abspath('.')):
	sub_path = filename.split(basedir)[-1]
	path = basedir + "/mungled"
	for dir in sub_path.split("/"):
		if not os.path.exists(path):
			os.mkdir(path, 0755)
		path = path + "/" + dir			
	return path
	
# Returns the position of the first isntance of any of the given arguments
def arg_from_commandline(arg):
	arg_list = arg if isinstance(arg, list) else [arg]
	for i in sys.argv:
		if i in arg_list:
			return sys.argv.index(i)+1
	

# Returns the position of the next cmdline argument
def next_cmdline_argument_pos(pos):
	if pos:
		for i in sys.argv[pos:]:
			if i.startswith("-"): #i.find("-") == 0:
				return sys.argv.index(i)


# Returns the parameters between an argument and the next from the cmdline
def parameters_from_commandline(arg):
	arg_pos =  arg_from_commandline(arg) 
	params = sys.argv[arg_pos:next_cmdline_argument_pos(
		arg_pos)] if arg_pos else []
	return params


def print_help():
	print """\
USAGE: python javascriptMungler.py [filenames].. [options]...\n\
Mungler for js, php, (p)html and css -files. \n\
Options:\n\
-i, --skipped FILES..\tList of filenames to be skipped \n\
-m, --map FILE \t\tUse a mapfile from a previous run \n\
-s, --soft FILES..\tMungles only identifiers in strings. Full pathname \n\
-n, --reserved FILES..\tReads a list of reserved words from a file \n\
-w, --identifiers IDS.. Does not mungle given identifiers
Switches:\n\
-r, --reverse \t\tRevert changes. \n\
-R, --recursive\t\tScans for files recursively starting from current path. \n\

Examples:\n\
\"-i vendor\"\n\t \
Skips files and subfolders under a \"vendor\"-dir. \n\
\"singlepage.html -m mapfileOfBigProject.txt\" \n\t \
Mungles a single file according to a previous run.\n\
\"jsclient.js -s serverpage.php\" \n\t \
Tries to sort out ajax-interoperability without messing backend files. \n\t \
Mungles any identifiers in jsclient.js, then searches serverpage.php for \n\t \
strings (only) and mungles any which are found as identifiers in jsclient.js. \
"""

def run_mungle(): 

	pwd = os.path.abspath(".")
	filenames_from_commandline = sys.argv[1:next_cmdline_argument_pos(1)]

	# convert given filenames to full paths. Horrible and untested, sorry
	for i, t in enumerate(filenames_from_commandline):
		if t is ".":
			filenames_from_commandline[i] = pwd
	filenames_from_commandline = map(lambda t: pwd +"/" + t if (
		t.find(pwd) < 0) else t, filenames_from_commandline) 

	# no files to mungle
	if not filenames_from_commandline:
			quit(print_help())

	# identifiers which should not be mungled
	global RESERVED_WORDS
	
	# reserved identifiers from given files
	for filename in parameters_from_commandline(["--reserved", "-n"]):
		RESERVED_WORDS += import_reserved(filename)

	# reserved identifiers from cmdline 
	RESERVED_WORDS += parameters_from_commandline(["--identifiers", "-w"])
	RESERVED_WORDS = tuple(RESERVED_WORDS)

	parser = TextParser(RESERVED_WORDS)
	parser.nominator = Nominator(RESERVED_WORDS)
	
	skipped_files = parameters_from_commandline([
			"--skipped",
			"--ignore", 
			"-i"])
	
	# These ought to get sorted out. I just tried to be fancy.
	skipped_files = map(lambda t: pwd +"/" + t if (
		t.find(pwd) < 0 and t.find("/") > -1) else t, skipped_files) 


	soft_treated_files = parameters_from_commandline([
			"--soft", 
			"-s"])
	soft_treated_files = map(lambda t: pwd +"/" + t if t.find(pwd) < 0 else 
		t, soft_treated_files) 

	skipped_files.extend(soft_treated_files)

	recursively = arg_from_commandline(["--recursive", "-R"])
		
	filepaths_to_mungle = []
	for t in filenames_from_commandline:
		if os.path.isfile(t):
			filepaths_to_mungle.append(t)
		if os.path.isdir(t):
			filepaths_to_mungle.extend(search_for_files(
				t, 
				skipped_files, 
				recursively))
	
	def parse_file(filename):
		if os.path.isfile(filename):
			textfile = open(filename, 'r')
			content = textfile.read()
			textfile.close()

			paate = filename.split(".")[-1]
			
			if paate not in ('phtml', 'html'):
				content = parser.remove_comments(content)
			content = parser.remove_console_rows(content)
			content = parser.parse(paate, content)
			content = parser.remove_empty_lines(content)
			mungled_textfile = open(
				file_export(filename), 'w+')

			if paate not in ('php', 'phtml', 'html'):
				mungled_textfile.write("\
/** Code mungled with JS-mungler (https://github.com/jraut/mungler) **/\n")
			mungled_textfile.write(content)
			mungled_textfile.close()

	for filename in filepaths_to_mungle:
		parse_file(filename)

	parser.soft = True
	for filename in soft_treated_files:
		parse_file(filename)

	for n, m in parser.nominator.nominations.iteritems():
		print n +": "+m


if (len(sys.argv) == 1):
	quit(print_help())
elif (arg_from_commandline(['--help'])):
	quit(print_help())
else:		
	run_mungle()


