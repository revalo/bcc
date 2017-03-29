import sys

from pycparser import parse_file, c_ast, c_generator
from pycparser.plyparser import Coord

def err(message):
	print "{0}: {1}".format(sys.argv[0], message)
	print "compilation terminated."
	exit()

class BetaGenerator(object):
	def __init__(self):
		self.registers = {}
		self.register_stack = []

	def visit(self, node):
		method = 'visit_' + node.__class__.__name__
		return getattr(self, method, self.generic_visit)(node)

	def i2r(self, index):
		return "R" + str(index)

	def r2i(self, r):
		return int(r.replace('R', ''))

	def assign_register(self, variable_name):
		used_registers = sorted([self.r2i(r) for r in self.registers.values()])
		if len(used_registers) == 0:
			my_register = self.i2r(1)
			self.registers[variable_name] = my_register
			return my_register

		for register, i in zip(used_registers, xrange(len(used_registers))):
			mod_i = i+1
			if not mod_i == register:
				my_register = self.i2r(mod_i)
				self.registers[variable_name] = my_register
				return my_register
		my_register = self.i2r(used_registers[-1]+1)
		self.registers[variable_name] = my_register
		return my_register


	def visit_BinaryOp(self, n):
		tl = type(n.left)
		tr = type(n.right)
		constant = ""
		if tl == c_ast.ID and tr == c_ast.ID:
			lr = self.registers[n.left.name]
			ll = self.registers[n.right.name]
			constant = ""
			
		if n.op == '+':
			frmt = "ADD{constant}({left}, {right}, {target})"
		if n.op == '-':
			frmt = "SUB{constant}({left}, {right}, {target})"
		if n.op == '*':
			frmt = "MUL{constant}({left}, {right}, {target})"
		if n.op == '/':
			frmt = "DIV{constant}({left}, {right}, {target})"


		return frmt.format(constant=constant,
						   left=ll,
						   right=lr,
						   target=self.register_stack.pop())


	def generic_visit(self, node):
		if node is None:
			return ''
		else:
			return ''.join(self.visit(c) for c_name, c in node.children())

	def visit_Decl(self, n, no_type=False):
		my_register = self.assign_register(n.name)
		if type(n.init) == c_ast.Constant:
			return "CMOVE({constant}, {register})".format(constant=n.init.value, register=my_register)
		if type(n.init) == c_ast.BinaryOp:
			self.register_stack.append(my_register)
			return self.visit(n.init)

	def visit_Constant(self, n):
		return n.value

	def visit_Compound(self, n):
		if n.block_items:
			return '\n'.join(self.visit(stmt) for stmt in n.block_items)
		return ""


def compile_ast(ast):
	# Find main
	main = None
	for func in ast.ext:
		if func.decl.name == "main":
			main = func
			break
	if main == None:
		err("fatal error: couldn't find entrypoint")

	walker = BetaGenerator()
	print walker.visit(main.body)

if __name__ == "__main__":
	if len(sys.argv) > 1:
		ast = parse_file(sys.argv[1])
		compile_ast(ast)
	else:
		err("fatal error: no input files")