import impmagic
import __main__

class EnvSettings:
	cache_dir = "~\\.config\\zpp_flow\\Cache"
	proxy = None
	full_log = False
	threading = True
	max_workers = 8

__main__.envsettings = EnvSettings()

#Création du context
class Context:
	@impmagic.loader(
		{'module':'os.path', 'submodule': ['dirname']},
		{'module': 'sys'},
		{'module':'core.structure', 'submodule': ['path_rep']},
	)
	def __init__(self, virtdir, virtname = None, prompt=None):
		self.env_dir = virtdir
		if virtname==None:
			name = virtdir.split(path_rep[0])
			self.env_name = name[len(name)-1]
		else:
			self.env_name = virtname

		if prompt!=None:
			self.prompt = f'({prompt}) '
		else:
			self.prompt = f'({self.env_name}) '

		self.executable = sys.executable
		self.python_dir = dirname(sys.executable)
		self.python_exe = sys.executable.replace(self.python_dir,"").replace(path_rep[0],"")
		if sys.platform == 'win32':
			self.bin_name = 'Scripts'
			self.lib_path = virtdir + path_rep[0] +'Lib'
			self.inc_path = virtdir + path_rep[0] +'Include'
		else:
			self.bin_name = 'bin'
			self.lib_path = virtdir + path_rep[0] +'lib'
			self.inc_path = virtdir + path_rep[0] +'include'
		self.bin_path = virtdir + path_rep[0] +self.bin_name
		self.env_exe = self.bin_path + path_rep[0] + self.python_exe
		self.env_exec_cmd = self.env_exe
		self.cfg_path = virtdir + path_rep[0] + 'pyvenv.cfg'


#Créer un environnement dans le cache
@impmagic.loader(
	{'module':'__main__'},
	{'module':'uuid', 'submodule': ['uuid1']},
	{'module':'os.path', 'submodule': ['expanduser','join']}
)
def create_temp_env(installmodule=None, upgradepip=True):
	name = str(uuid1())
	cachedir = join(expanduser(__main__.envsettings.cache_dir), name)
	__main__.ToDoClear.append(cachedir)
	create_environment(cachedir, name=name, installmodule=None, upgradepip=upgradepip, prompt="temp-"+name)

	return name, cachedir


#Création d'un environnement
@impmagic.loader(
	{'module':'__main__'},
	{'module':'os.path', 'submodule': ['exists', 'isdir']},
	{'module':'os'},
	{'module':'virtualenv'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'sys'},
	{'module':'core.structure', 'submodule': ['path_rep', 'path_reg']},
)
def create_environment(virtdir, name=None, installmodule=None, clear=False, upgradepip=True, symlinks=False, sitepackages=False, proxy=None, prompt=None):
	if proxy==None:
		proxy = __main__.envsettings.proxy
		if proxy=="":
			proxy=None
	if name!=None:
		logs(f"Environnement {name}")
	else:
		logs(f"Environnement {virtdir}")

	logs("Création du contexte")
	virtdir = path_reg(virtdir)
	context = Context(virtdir, name, prompt=prompt)

	args = []
	args.append("--no-download")
	args.append("--no-periodic-update")
	#args.append("--no-setuptools")
	#args.append("--no-pip")
	#args.append("--no-wheel")

	if not symlinks:
		args.append("--always-copy")
	
	if sitepackages:
		args.append("--system-site-packages")

	if clear:
		args.append("--clear")

	if prompt is not None:
		args.extend(["--prompt", prompt])

	#args.append("--python")
	#args.append("PATHPYTHON")
	args.append(context.env_dir)

	if clear==False and exists(virtdir) and isdir(virtdir) and len(os.listdir(virtdir))!=0:
		logs("Le dossier n'est pas vide", "warning")
		sys.exit()
	
	logs("Création de l'environnement")
	try:
		virtualenv.cli_run(args)
	except Exception as err:
		logs(err, "error")

	if not exists(context.bin_path) or not exists(context.lib_path):
		logs("ERREUR: Le dossier de l'environnement n'a pas été créé", "error")
		sys.exit()
	
	if not exists(context.cfg_path):
		logs("ERREUR: Le fichier de config n'a pas été créé", "error")
		sys.exit()
	
	if not exists(context.env_exe):
		logs("ERREUR: L'exécutable n'a pas été copié", "error")
		sys.exit()
	
	if not exists(context.bin_path+path_rep[0]+"activate"):
		logs("ERREUR: Les scripts d'activation n'ont pas été créé", "error")
		sys.exit()

	if os.name=='nt':
		pipname = 'pip.exe'
	else:
		pipname = 'pip'
	if not exists(context.bin_path+path_rep[0]+pipname):
		logs("ERREUR: Pip n'a pas été installé", "error")
		sys.exit()

	if upgradepip:
		logs("Recherche de mise à jour")
		upgrade_module(context.env_exe,"pip", proxy=proxy)
		upgrade_module(context.env_exe,"setuptools", proxy=proxy)

	if installmodule!=None:
		install_pool(context.env_exe, installmodule, proxy)

	logs("Environnement créé", "success")

	venv_data = {}
	venv_data['env_dir'] = context.env_dir 
	venv_data['env_name'] = context.env_name 
	venv_data['env_exe'] = context.env_exe
	venv_data['bin_path'] = context.bin_path

	return venv_data


#Suppression d'un environnement
@impmagic.loader(
	{'module':'os.path', 'submodule': ['exists']},
	{'module':'shutil', 'submodule': ['rmtree']},
	{'module':'app.logs', 'submodule': ['logs']}
)
def remove_environment(virtdir):
	if exists(virtdir):
		logs("Suppresion d'un dossier d'environnement")
		try:
			rmtree(virtdir)
		except PermissionError:
			logs("ERREUR: Autorisation refusée pour supprimer le dossier d'environnement", "error")
		except Exception as err:
			logs(f"Error: {err}", "error")
	else:
		logs("Le dossier d'environnement n'existe pas", "error")

#Upgrade d'un module dans un environnement
@impmagic.loader(
	{'module':'__main__'},
	{'module':'subprocess'},
	{'module':'chardet'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'core.structure', 'submodule': ['path_rep']},
	{'module':'core.sandbox.package', 'submodule': ['get_package']},
)
def upgrade_module(env_exe, namemodule, version=None, proxy=None, force=False, reinstall=False):
	logs(f"Mise à jour du module {namemodule}")

	env_exe = env_exe.replace(path_rep[1], path_rep[0])

	if version!=None:
		for_install = namemodule+"=="+version
	else:
		for_install = namemodule

	find = get_package(env_exe, namemodule)
	if find!=False:
		find = find.replace("==","")
		if version!=None and find==version:
			#logs(f"Module {namemodule} déjà installé dans la bonne version")
			return True

	if proxy==None:
		proxy = __main__.envsettings.proxy
		if proxy=="":
			proxy=None

	if namemodule!="pip" and namemodule!="setuptools":
		if get_package(env_exe, namemodule)==False:
			logs(f"Module {namemodule} non installé", "warning")
			return

	cmd = [env_exe, '-m', 'pip', 'install', for_install, '--upgrade']
	if proxy!=None:
		cmd.append('--proxy='+proxy)

	if force==True:
		cmd.append('--force')
	
	if reinstall==True:
		cmd.append('--force-reinstall')

	full_log = __main__.envsettings.full_log

	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	while True:
		output = proc.stdout.readline().decode("utf-8").strip()
		if output == "":
			break
		if full_log:
			logs(output)

	d_error = False
	#Pour éviter les erreurs sur un pip pas à jour
	stderrr = proc.stderr.read()
	if stderrr!=None:
		if chardet.detect(stderrr)['encoding']!=None and "A new release of pip available" not in stderrr.decode(chardet.detect(stderrr)['encoding']).strip():
			proc.stderr.seek(0)
			for output in proc.stderr.readlines():
				if len(output)>0 and d_error==False:
					logs(f"ERREUR: Module {namemodule} non mis à jour\nMessage d'erreur: {proc.stderr.readlines()}", "error")
					d_error=True

				if full_log:
					logs(output.decode("utf-8").strip(), "error")

	if d_error==False:
		logs(f"Module {namemodule} mis à jour")
		return True

	return False

#Installation de package en multithread si enable
@impmagic.loader(
	{'module':'__main__'},
	{'module':'concurrent.futures', 'as': 'worker'},
	{'module':'core.structure', 'submodule': ['path_rep']},
)
def install_pool(env_exe, installmodule, proxy=None, force=False):
	env_exe = env_exe.replace(path_rep[1], path_rep[0])

	if __main__.envsettings.threading:
		threads = []

		with worker.ThreadPoolExecutor(max_workers=__main__.envsettings.max_workers) as executor:
			futures = []
			for package in installmodule:
				futures.append(executor.submit(install_module, env_exe, package, proxy, force))
			
			worker.wait(futures)

	else:
		for package in installmodule:
			install_module(env_exe, package, proxy=proxy, force=force)


#Installation d'un module dans un environnement
@impmagic.loader(
	{'module':'__main__'},
	{'module':'subprocess'},
	{'module':'chardet'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'re', 'submodule': ['compile']},
	{'module':'core.sandbox.package', 'submodule': ['get_package', 'package_regex']},
)
def install_module(env_exe, namemodule, proxy=None, force=False):
	if proxy==None:
		proxy = __main__.envsettings.proxy
		if proxy=="":
			proxy=None

	package_compiled = compile(package_regex)
	package_match = package_compiled.search(namemodule)
	if package_match!=None:
		namemodule = package_match.group('name')
		namemodule = namemodule.lower().replace("-","_")
		version = package_match.group('version')

	else:
	   	logs(f"Nom du module {namemodule} invalide", "error")
	   	return

	if namemodule!="pip" and namemodule!="setuptools":
		find = get_package(env_exe, namemodule)
		if find!=False:
			find = find.replace("==","")
			if version:
				if find==version:
					pass
					#logs(f"Module {namemodule} déjà installé dans la bonne version", "warning")
				else:
					#logs(f"Module {namemodule} déjà installé dans la version ({find})", "error")

					if force==True:
						logs("Mise à jour forcée du module", "warning")
						upgrade_module(env_exe, namemodule, version=version,force=True)
			else:
				#logs(f"Module {namemodule} déjà installé", "warning")
				if force==True:
					logs("Mise à jour forcée du module", "warning")
					upgrade_module(env_exe, namemodule, version=None,force=True)

			return
	
	if version:
		namemodule = f"{namemodule}{version}"
	logs(f"Installation du module {namemodule}")
	cmd = [env_exe, '-m', 'pip', 'install', namemodule]
	if proxy!=None:
		cmd.append('--proxy='+proxy)

	full_log = __main__.envsettings.full_log

	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	while True:
		output = proc.stdout.readline().decode("utf-8").strip()
		if output == "":
			break
		if full_log:
			logs(output)

	d_error = False
	#Pour éviter les erreurs sur un pip pas à jour
	stderrr = proc.stderr.read()
	if stderrr!=None:
		if chardet.detect(stderrr)['encoding']!=None and "A new release of pip available" not in stderrr.decode(chardet.detect(stderrr)['encoding']).strip():
			proc.stderr.seek(0)
			for output in proc.stderr.readlines():
				if len(output)>0 and d_error==False:
					logs(f"ERREUR: Module {namemodule} non installé\nMessage d'erreur: {output.decode()}", "error")
					d_error=True

				if full_log:
					logs(output.decode("utf-8").strip(), "error")

	if not d_error:
		logs(f"Module {namemodule} installé", "success")


#Ouvrir l'environnement
@impmagic.loader(
	{'module':'os.path', 'submodule': ['exists', 'isdir']},
	{'module':'os', 'submodule': ['name', 'environ']},
	{'module':'subprocess'},
	{'module':'pexpect'},
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'sys'},
	{'module':'core.structure', 'submodule': ['path_rep', 'path_reg', 'get_os']},
)
def open_environment(virtdir, projectfolder="", shell=False):
	context = Context(path_reg(virtdir))

	if exists(context.bin_path) and isdir(context.bin_path):
		if shell:
			cmd = context.env_exe
		else:
			OSType = get_os()
			if OSType=='cmd' or OSType=='cmd.exe':
				activate_file='activate.bat'
				if exists(context.bin_path+path_rep[0]+activate_file):
					cmd = ['cmd', '/k']
					target = ""
					target+="pushd "+context.bin_path.replace(path_rep[1], path_rep[0])+" & .\\"+activate_file+" & popd"
					cmd.append(target)
				else:
					logs("ERREUR: Le script d'activation n'existe pas", "error")
					sys.exit()

			elif OSType=='powershell.exe' or name=='nt':
				activate_file='activate.ps1'
				if exists(context.bin_path+path_rep[0]+activate_file):
					cmd = ['powershell', '-NoExit', '-Command']
					target = ""
					target+='. "'+context.bin_path+path_rep[0]+activate_file+'"'

					cmd.append(target)
				else:
					logs("ERREUR: Le script d'activation n'existe pas", "error")
					sys.exit()
			
			else:
				activate_file='activate'
				if exists(context.bin_path+path_rep[0]+activate_file):

					cmd = []
					target = ""
					target=". "+context.bin_path+path_rep[0]+activate_file

					shell = environ.get('SHELL')
					interact = pexpect.spawn(shell, ['-i'])
					interact.sendline(target)
					interact.interact(escape_character=None)

					interact.close()
					return
				else:
					logs("ERREUR: Le script d'activation n'existe pas", "error")
					sys.exit()

		subprocess.call(cmd, shell=True)
	else:
		logs("ERREUR: Dossier d'environnement introuvable", "error")

#Parse des arguments envoyés
def arg_parse(string):
	array = []

	if len(string)>=1:
		arg = ""
		lock = None
		if isinstance(string, list):
			string = " ".join(string)
		for i,caracter in enumerate(string):
			if (caracter=="'" or caracter=='"') and (lock==None or caracter==lock):
				if lock==None:
					lock=caracter
				else:
					array.append(arg)
					arg=""
					lock=None
			else:
				if caracter==" " and lock!=None:
					arg+=caracter
				elif caracter==" " and len(arg)>=1 and lock==None:
					array.append(arg)
					arg=""
				elif caracter!=" ":
					arg+=caracter
					if i==len(string)-1:
						array.append(arg)
						arg=""
	return array

#Appel d'une commande dans un environnement
@impmagic.loader(
	{'module':'subprocess'},
	{'module': 'time', 'submodule': ['perf_counter']},
	{'module': 'datetime', 'submodule': ['timedelta', 'time']},
)
def command_shell(env_exe, command, args=None, timer=False):
	if isinstance(command, list):
		if command[0]=="python":
			command.pop(0)
		cmd = [env_exe] + command

	else:
		if command.startswith("python "):
			cmd = [env_exe, command.replace("python ","")]
		else:
			cmd = [env_exe, '-c', command]

	if args!=None and len(args)>0:
		if isinstance(args, str):
			cmd = cmd+arg_parse(args)
		if isinstance(args, list):
			cmd = cmd+args
	
	if timer:
		proc = subprocess.Popen(cmd, shell=True)
		
		st = perf_counter()

		proc.communicate()

		et = perf_counter()
		duree = timedelta(seconds=(et - st))
		print(f" Days		  : {duree.days}\n Hours		: {duree.seconds//3600}\n Minutes	  : {duree.seconds%3600//60}\n Seconds	  : {duree.seconds%60}\n Milliseconds : {duree.microseconds//1000}\n Ticks		: {duree.microseconds*10}")
	else:
		proc = subprocess.Popen(cmd, shell=True)
		proc.communicate()
