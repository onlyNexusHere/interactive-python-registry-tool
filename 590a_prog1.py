

import sys
sys.path.insert(0, 'python-registry-1.2.0')

from Registry import *

newFile = None

def rec(key, f, level=0):
    """
    Recurses across all RegistryKeys and applies the function f.
    key : A Registry.RegistryKey
    f : A function taking one argument, a Registry.RegistryKey
    returns : None
    """
    f(key, tabs=level)
    for subkey in key.subkeys():
    	rec(subkey, f, level=level+1)

def print_all(key, tabs):
	print "\t" * tabs + key.path()

def write_all_keys(key, tabs=0):
    """
    Writes the path of a RegistryKey.
    key : A Registry.RegistryKey
    returns : None
    """
  
    newFile.write("\n" + "\t" * tabs + key.path())

def find_microsoft(key, tabs):
    """
    Prints Registry keys whose values contain the string "microsoft".
    key : A Registry.RegistryKey
    returns : None
    """
    for value in [v.value() for v in key.values() \
					if v.value_type() == Registry.RegSZ \
					or v.value_type() == Registry.RegExpandSZ]:
    	if "microsoft" in value:
    		print key.path()

def new_reg(f0, reg0, filename):
	if f0 is not None:
		f0.close()
	f0 = open(filename, "rb")
	reg0 = Registry.Registry(f0)
	return f0, reg0

def find_string_in_name(reg, input_string):
	"""
	This method is very similar to a file from the guy who made python-registry, because my own trials were not working.
	"""

	paths = []
	value_names = []
	values = []
	case_insensitive = True
	query = input_string

	def rec(key, depth, needle):
		for value in key.values():
			if (case_insensitive and needle in value.name().lower()) or needle in value.name():
				value_names.append((key.path(), value.name()))
				sys.stdout.write("n")
				sys.stdout.flush()
			try:
				if (case_insensitive and needle in str(value.value()).lower()) or needle in str(value.value()):
					values.append((key.path(), value.name()))
					sys.stdout.write("v")
					sys.stdout.flush()
			except UnicodeEncodeError:
				pass
			except UnicodeDecodeError:
				pass

		for subkey in key.subkeys():
			if needle in subkey.name():
				paths.append(subkey.path())
				sys.stdout.write("p")
				sys.stdout.flush()
			rec(subkey, depth + 1, needle)

	needle = query
	if case_insensitive:
		needle = needle.lower()

	rec(reg.root(), 0, needle)
	print("")

	print("[Paths]")
	for path in paths:
		print("  - %s" % (path))
	if len(paths) == 0:
		print("  (none)")
	print("")

	print("[Value Names]")
	for pair in value_names:
		print("  - %s : %s" % (pair[0], pair[1]))
	if len(value_names) == 0:
		print("  (none)")
	print("")

	print("[Values]")
	for pair in values:
		print("  - %s : %s" % (pair[0], pair[1]))
	if len(values) == 0:
		print("  (none)")
	print("")

f = open("ntuser.dat", "rb")
# reg = Registry.Registry(f)
# newFile.write("\nNTUSER.DAT")
# rec(reg.root(),write_all_keys)
# f.close()

input = ""
reg = None
print "Welcome! Please choose a registry file, and then you can view the contents or find the values from a path. Use h for help."
input = raw_input(">> ")
while input.strip() != "quit":
	if input.strip() == "h" or input.strip() == "help":
		print "This is the help section."
		print "use <file_name> : Use this command to switch registry files."
		print "\tOptional file names are ntuser.dat, system, sam, security, software."
		print "content : Use this to see all possible names to the "
		print "search <path_name> : Use this to find the value with a path. You many need two backslashs."
		print "key <query> : Search for a string the registry hive."
		print "write <new_file_name> : Use this to stuff in content into an out file."
		print "quit : To quit the program."
	elif input.strip()[0:len("use")] == "use":
		if "system" in input.strip()[len("use"):]:
			f, reg = new_reg(f, reg, "system")
		elif "sam" in input.strip()[len("use"):]:
			f, reg = new_reg(f, reg, "sam")
		elif "security" in input.strip()[len("use"):]:
			f, reg = new_reg(f, reg, "security")
		elif "ntuser.dat" in input.strip()[len("use"):]:
			f, reg = new_reg(f, reg, "ntuser.dat")
		elif "software" in input.strip()[len("use"):]:
			f, reg = new_reg(f, reg, "software")
		else:
			print "Not a file, try again"
	elif input.strip()[0:len("content")] == "content":
		if reg is not None:
			rec(reg.root(), print_all)
		else:
			print "Please pick a file."
	elif input.strip()[0:len("write")] == "write":
		if reg is not None:
			newFileName = input.strip()[len("write "):]
			print "Writing to file " + newFileName
			if newFileName != None:
				newFile = open(newFileName, "w")
				rec(reg.root(), write_all_keys)
				newFile.close()
			else:
				print "Improper name. Try again."
		else:
			print "Please pick a file."
	elif input.strip()[0:len("search")] == "search":
		if reg == None:
			print "You need to choose a file."
			break

		filepath = input.strip()[len("search "):]
		
		print "Looking for "+ filepath

		key = None

		try:
			key = reg.open(filepath)

		except Registry.RegistryKeyNotFoundException:
			print "Couldn't find Run key. Exiting..."
			continue
		
		try:
			for value in [v for v in key.values() \
						if v.value_type() == Registry.RegSZ or \
						v.value_type() == Registry.RegExpandSZ]:
				print "%s: %s" % (value.name(), value.value())
		except AttributeError:
			print "Sorry, something went wrong."
	
	elif input.strip()[0:len("key")] == "key":
		if reg == None:
			print "You need to choose a file."
			break

		key_query = input.strip()[len("key "):]
		
		print "Looking for "+ key_query

		find_string_in_name(reg, key_query)

	else:
		print "Type help for help or quit to quit."

	input = raw_input(">> ")

print "Goodbye!"

if f is not None:
	f.close()

if newFile is not None:
	newFile.close()

