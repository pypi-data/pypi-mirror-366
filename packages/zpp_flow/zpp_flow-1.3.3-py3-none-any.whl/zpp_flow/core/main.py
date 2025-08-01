import impmagic
import __main__
import atexit
import signal

__main__.ToDoClear = []

@impmagic.loader(
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'os.path', 'submodule': ['basename', 'exists', 'isdir', 'isfile']},
	{'module':'shutil', 'submodule': ['rmtree']},
	{'module':'os', 'submodule': ['remove']}
)
def clear_env():
	for file in __main__.ToDoClear:
		if exists(file):
			logs(f"Suppression de l'environnement {basename(file)}")
			if isdir(file):
				rmtree(file)
			elif isfile(file):
				remove(file)

def handler_signal(signal_num, frame):
	atexit._run_exitfuncs()


atexit.register(clear_env)
signal.signal(signal.SIGINT, handler_signal)


class Flow:
	@impmagic.loader(
		{'module':'os'},
		{'module':'zpp_config', 'submodule': ['Config']},
		{'module':'os.path', 'submodule': ['abspath', 'expanduser', 'exists', 'join', 'dirname']}
	)
	def __init__(self):
		if os.name=="nt":
			self.flow_folder = expanduser("~\\.config\\zpp_flow\\.config")
		else:
			self.flow_folder = expanduser("~/.config/zpp_flow/.config")

		self.ini_file = join(self.flow_folder,"flow.ini")

		if not exists(self.ini_file):
			if not exists(self.flow_folder):
				os.makedirs(self.flow_folder)
			print("Création du fichier de config")
			self.conf = Config(self.ini_file, auto_create = True)
			if os.name=="nt":
				self.conf.add(val="flow_fabric", key=join("~\\.config\\zpp_flow\\.config", "fabric"), section="general")
			else:
				self.conf.add(val="flow_fabric", key=join("~/.config/zpp_flow/.config", "fabric"), section="general")

		else:
			self.conf = Config(self.ini_file)

		#Création du répertoire fabric s'il n'existe pas
		self.flow_fabric = expanduser(self.conf.load('flow_fabric', section='general'))
		if not exists(self.flow_fabric):
			os.makedirs(self.flow_fabric)


	@impmagic.loader(
		{'module':'os'}
	)
	def open_fabric(self):
		os.startfile(self.flow_fabric)


	@impmagic.loader(
		{'module':'app.logs', 'submodule': ['logs', 'print_nxs']},
		{'module':'core.runner', 'submodule': ['run_func']},
		{'module':'internal_fabric.analyse', 'submodule': ['tree_plugin']},
		{'module':'datetime', 'submodule': ['datetime']},
		{'module':'time'},
		{'module':'re'}
	)
	def start(self, task_name, parameter, only_task=False, only_flow=False, starter=None, repeat=None, debug=False, is_sandbox=False, verbose=False, timer=False, identity=False):
		data = tree_plugin(self.flow_fabric)
		
		task_data = None

		if parameter[0] in data['flow'] and (only_flow or (not only_task and not only_flow)):
			task_data = data['flow'][parameter[0]]
		
		if parameter[0] in data['task'] and (only_task or (not only_task and not only_flow)):
			task_data = data['task'][parameter[0]]

		if task_data and len(task_data):
			if starter:
				matcher_starter = re.match(r"^(?P<starter_hour>\d{2}):(?P<starter_minute>\d{2})(:(?P<starter_second>\d{2}))?$", starter)
				if matcher_starter:
					wait = True
					logs(f"Démarrage à {starter}")
					while wait:
						now = datetime.now()

						if now.hour==int(matcher_starter.group('starter_hour')) and now.minute==int(matcher_starter.group('starter_minute')) and (not matcher_starter.group('starter_second') or now.second==int(matcher_starter.group('starter_second'))):
							wait=False
						else:
							time.sleep(1)

				else:
					logs("Format started invalide", "critical")
					return

			if 'is_task' in task_data[0] and task_data[0]['is_task']:
				rtype = "task"
			else:
				rtype = "flow"

			if repeat:
				matcher = re.match(r"^(?P<repeat_value>\d{1,})(?P<repeat_type>(s|m|h|d)?)$", repeat)
				if matcher:
					timer_wait = int(matcher.group('repeat_value'))

					if matcher.group('repeat_type'):
						if matcher.group('repeat_type')=="m":
							timer_wait *= 60
						elif matcher.group('repeat_type')=="h":
							timer_wait *= 3600
						elif matcher.group('repeat_type')=="d":
							timer_wait *= 86400

					try:
						while True:
							if rtype=="task":
								print_nxs(f"Démarrage de la task {task_name}", color="magenta")
							else:
								if verbose:
									print_nxs(f"Démarrage du flow {task_name}", color="magenta")
							run_func(rtype, task_name, task_data, parameter, self.flow_fabric,debug=debug, is_sandbox=is_sandbox, verbose=verbose, timer=timer, identity=identity)
							print_nxs(f"Attente de la prochaine itération", color="magenta")
							time.sleep(timer_wait)
					except KeyboardInterrupt:
						logs("Arrêt demandé")
				else:
					logs("Format de repeat invalide", "critical")
			else:
				if rtype=="task":
					print_nxs(f"Démarrage de la task {task_name}", color="magenta")
				else:
					print_nxs(f"Démarrage du flow {task_name}", color="magenta")
				run_func(rtype, task_name, task_data, parameter, self.flow_fabric, debug=debug, is_sandbox=is_sandbox, verbose=verbose, timer=timer, identity=identity)

		else:
			logs(f"task {task_name} non trouvé", "warning")


	#Afficher la liste des task et flow
	@impmagic.loader(
		{'module':'internal_fabric.analyse', 'submodule': ['tree_plugin']}
	)
	def list(self):
		data = tree_plugin(self.flow_fabric)

		return data['task'].keys(), data['flow'].keys()


	#Afficher le détail des task et flow
	@impmagic.loader(
		{'module':'internal_fabric.analyse', 'submodule': ['tree_plugin']}
	)
	def details(self):
		return tree_plugin(self.flow_fabric)


	@impmagic.loader(
		{'module':'internal_fabric.fabric', 'submodule': ['pull_code']}
	)
	def pull_fabric(self, filename, output=None):
		pull_code(filename, self.flow_fabric, output)


	@impmagic.loader(
		{'module':'internal_fabric.fabric', 'submodule': ['push_code']}
	)
	def push_fabric(self, filename, dest=None):
		push_code(filename, self.flow_fabric, dest)


	@impmagic.loader(
		{'module':'internal_fabric.fabric', 'submodule': ['pop_code']}
	)
	def pop_fabric(self, filename):
		pop_code(filename, self.flow_fabric)
