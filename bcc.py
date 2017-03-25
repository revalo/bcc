import sys

from pycparser import parse_file, c_ast, c_generator
from pycparser.plyparser import Coord

def err(message):
	print "{0}: {1}".format(sys.argv[0], message)
	print "compilation terminated."
	exit()

def compile_ast(ast):
	# Find main
	main = None
	for func in ast.ext:
		if func.decl.name == "main":
			main = func
			break
	if main == None:
		err("fatal error: couldn't find entrypoint")

	pgm = []
	pgm.append("_main:") # Program block always starts at label _main

	register_table = {}
	register_count = 0

	for inst in main.body.block_items:
		inst.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ast = parse_file(sys.argv[1])
        print compile_ast(ast)
    else:
    	err("fatal error: no input files")