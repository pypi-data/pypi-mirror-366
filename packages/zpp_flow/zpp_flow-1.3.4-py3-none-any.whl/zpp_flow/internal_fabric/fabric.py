import impmagic

def print_pattern(index, max, arbo):
	arbo = "".join(arbo)
	if index==max-1:
		print(f"{arbo}└─", end="")
	else:
		print(f"{arbo}├─", end="")
	

@impmagic.loader(
	{'module': 'os.path','submodule': ['isfile', 'isdir']},
	{'module': 'glob','submodule': ['glob']},
	{'module': 'zpp_color','submodule': ['fg','bg','attr']}
)
def show_tree(path, string="", lvl=0, arbo_display=[]):
	arbo = []

	content = glob(f"{path}/*")

	for rep in content:
		rep = rep.replace("\\", "/")
		file = (rep.split("/"))[rep.count("/")]

		if isdir(rep)==True:
			arbo.append({'name': file, 'type': 'dir'})
		elif isfile(rep)==True:
			arbo.append({'name': file, 'type': 'file'})

	arbo = sorted(arbo, key=lambda x: x['name'])
	arbo = sorted(arbo, key=lambda x: x['type'])
	
	for i, element in enumerate(arbo):
		if element['name']!="__pycache__":
			print_pattern(i, len(content), arbo_display)
			if element['type']=='dir':
				print(f'{fg("cyan")}{element["name"]}\n{attr("reset")}',end="")
				if i==len(content)-1:
					new_arbo = arbo_display+['   ']
				else:
					new_arbo = arbo_display+['│  ']

				show_tree(path + "/" + element['name'],string, lvl+1, arbo_display=new_arbo)
			else:
				if element['name'].endswith(".py"):
					print(f'{fg("magenta")}{element["name"]}\n{attr("reset")}',end="")
				else:
					print(f'{fg("dark_gray")}{element["name"]}\n{attr("reset")}',end="")


@impmagic.loader(
	{'module':'zpp_args'},
	{'module':'sys'},
	{'module':'shutil'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'os.path', 'submodule': ['join', 'exists', 'isdir', 'basename', 'expanduser']}
)
def pull_code(filename, flow_fabric, output=None):
	file_path = join(flow_fabric, filename)
	if exists(file_path):
		if output:
			output = expanduser(output)
		else:
			output = basename(file_path)

		try:
			if isdir(file_path):
				shutil.copytree(file_path ,output)
			else:
				shutil.copy2(file_path ,output)
		except Exception as err:
			logs(f"Erreur lors de la copie: {err}", "critical")
	else:
		logs("Le fichier n'existe pas", "critical")


@impmagic.loader(
	{'module':'zpp_args'},
	{'module':'sys'},
	{'module':'shutil'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'os', 'submodule': ['makedirs']},
	{'module':'os.path', 'submodule': ['join', 'exists', 'isdir', 'basename', 'dirname', 'expanduser']}
)
def push_code(filename, flow_fabric, dest=None):
	file_path = expanduser(filename)

	if exists(file_path):
		if dest:
			dest = join(flow_fabric, dest)
		else:
			dest = join(flow_fabric, basename(file_path))

		try:
			if not exists(dirname(dest)):
				makedirs(dirname(dest))
		except Exception as err:
			logs(f"Erreur lors de la création du répertoire de destination: {err}", "critical")

		try:
			if isdir(file_path):
				shutil.copytree(file_path ,dest)
			else:
				shutil.copy2(file_path ,dest)
		except Exception as err:
			logs(f"Erreur lors de la copie: {err}", "critical")
	else:
		logs("Le fichier n'existe pas", "critical")


@impmagic.loader(
	{'module':'shutil'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'os', 'submodule': ['remove']},
	{'module':'os.path', 'submodule': ['join', 'exists', 'isdir', 'basename', 'dirname', 'expanduser']}
)
def pop_code(filename, flow_fabric):
	file_path = join(flow_fabric, filename)
	if exists(file_path):
		try:
			if isdir(file_path):
				shutil.rmtree(file_path)
			else:
				remove(file_path)
		
		except Exception as err:
			logs(f"Erreur lors de la suppression: {err}", "critical")
	else:
		logs("Le fichier n'existe pas", "critical")


@impmagic.loader(
	{'module':'glob', 'submodule': ['glob']},
	{'module':'os.path', 'submodule': ['isfile']}
)
def tree_fabric(dirname):
	content = []
	for file in glob(f"{dirname}/*"):
		if isfile(file):
			if file.endswith(".py") or file.endswith(".pyw"):
				content.append(file)
		else:
			content+=tree_fabric(file)

	return content