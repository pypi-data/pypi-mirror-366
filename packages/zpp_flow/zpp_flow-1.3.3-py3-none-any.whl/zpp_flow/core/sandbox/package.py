import impmagic

dependencies_regex = r'^([a-zA-Z0-9_.-]+)((>=|!=|<=|<|>|\^|==)\s*\d+(\.\d+(\.\d+)?)?)?$'
package_regex = r"(?P<name>^([a-zA-Z0-9_.-]+))\s?\(?(?P<version>(>=|!=|<=|<|>|\^|==)\s*\d+(\.\d+){0,2},?\s?((>=|!=|<=|<|>|\^|==)\s*\d+(\.\d+){0,2})*)?"


#Retourne la liste des packages installés
@impmagic.loader(
	{'module':'subprocess'},
	{'module':'re', 'submodule': ['compile']},
	{'module':'core.structure', 'submodule': ['path_rep']},
)
def get_all_package(env_exe, clean_name=False):
	env_exe = env_exe.replace(path_rep[1], path_rep[0])
	stdout = []

	cmd = [env_exe, '-m', 'pip', 'freeze']
	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()

	stdout = stdout.decode('utf-8').split("\r\n")
	result = {}

	for pack in stdout:
		if len(pack):
			pack = pack.split("==")
			if len(pack)>1:
				if clean_name:
					result[pack[0].replace("-", "_")] = pack[1]
				else:
					result[pack[0]] = pack[1]

	return result



#Check si le package est déjà installé
@impmagic.loader(
	{'module':'__main__'},
	{'module':'subprocess'},
	{'module':'re', 'submodule': ['compile']},
	{'module':'core.structure', 'submodule': ['path_rep']},
)
def get_package(env_exe, namemodule):
	env_exe = env_exe.replace(path_rep[1], path_rep[0])

	reg = compile(dependencies_regex)
	package_compiled = compile(package_regex)
	package_match = package_compiled.search(namemodule)
	if package_match!=None:
		namemodule = package_match.group('name')
		namemodule = namemodule.lower().replace("-","_")
		version = package_match.group('version')

	else:
	   	logs(f"Nom du module {namemodule} invalide", "error")
	   	return

	#Vérifie si le retour commande pip freeze existe déjà (pour éviter de l'appeler plusieurs fois)
	if not hasattr(__main__, 'already_installed'):
		#cmd = [env_exe, '-c', 'from pip._internal.operations import freeze;print("\\n".join([ package for package in freeze.freeze()]));']
		#cmd = [env_exe, '-c', 'from pkg_resources import working_set;print("\\n".join([package.project_name + "==" + package.version for package in working_set]))']
		cmd = [env_exe, '-m', 'pip', 'freeze']
		proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		__main__.already_installed = stdout
	else:
		stdout = __main__.already_installed

	for pack in stdout.decode().split("\r\n"):
		if pack!="":
			pack = pack.lower()
			module_installed = reg.match(pack.replace("-","_"))
			if module_installed!=None and namemodule==module_installed.group(1):
				return module_installed.group(2)
	return False

