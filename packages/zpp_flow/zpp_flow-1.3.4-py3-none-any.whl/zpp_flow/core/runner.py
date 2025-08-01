import impmagic
import json
import sys
import base64

@impmagic.loader(
	{'module':'__main__'},
)
def set_persist(key, value):
    __main__.context_args[key] = value

@impmagic.loader(
	{'module':'__main__'},
)
def get_persisted_context():
    return __main__.context_args

@impmagic.loader(
	{'module':'__main__'},
)
def clear_persisted_context():
    __main__.context_args = {}


@impmagic.loader(
	{'module':'__main__'},
	{'module':'app.logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def parse_arguments(proc_arguments, parameters):
	"""
	Parse les paramètres en arguments nommés et positionnels.
	
	proc_arguments : [('arg1',), ('arg2', default), ...]
	parameters : liste d'objets de types variés (str, int, float, bytes, etc)
	
	Retourne dict avec les arguments prêts pour appel fonction.
	"""
	#if persisted_args is None:
	if hasattr(__main__, "context_args"):
		persisted_args = __main__.context_args
	else:
		persisted_args = {}

	c_args = {}
	c_params = []

	for p in parameters:
		# On peut reconnaître un argument nommé uniquement si p est str et contient '='
		if isinstance(p, str) and "=" in p:
			k, v = p.split("=", 1)
			c_args[k.strip()] = v.strip()  # Note: v reste une str ici, conversion possible à faire plus tard si besoin
		else:
			c_params.append(p)

	args_function = {}

	for a in proc_arguments:
		name = a[0]
		has_default = len(a) > 1
		default = a[1] if has_default else None

		if name in c_args:
			# Ici c_args[name] est une str, on pourrait tenter une conversion automatique (optionnel)
			args_function[name] = c_args[name]
		elif name in persisted_args:
			args_function[name] = persisted_args[name]
		elif c_params:
			args_function[name] = c_params.pop(0)
		elif has_default:
			# même si default est None, on considère qu'on doit prendre la valeur par défaut
			args_function[name] = default
		else:
			# Demande à l'utilisateur la valeur manquante
			user_input = input(f"{name}: ")
			args_function[name] = user_input

	return args_function



@impmagic.loader(
	{'module':'app.logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def run_task(task_name, data, parameter, flow_fabric, debug=False, verbose=False):
	def show_debug(result):
		if debug:
			print_nxs(f"Result: ", color="yellow", nojump=True)
			print_nxs(result, color="dark_gray")

	for proc in data:
		if 'path' in proc:
			mod_file = impmagic.get_from_file(join(flow_fabric, proc['path']))
			func = getattr(mod_file, proc['func_name'])

			if verbose:
				logs(f"Démarrage de la fonction {proc['func_name']}", "info")

			if len(proc['arguments']):
				try:
					args_function = parse_arguments(proc['arguments'], parameter[1:])
					result = func(**args_function)
					show_debug(result)
				except ValueError as e:
					logs(f"task {task_name}: {e}", "warning")
			else:
				result = func()
				show_debug(result)
		else:
			logs(f"task {task_name}: path non identifié", "warning")


@impmagic.loader(
	{'module':'__main__'},
	{'module':'app.logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def run_flow(task_name, data, parameter, flow_fabric, debug=False, verbose=False):
	def show_debug(result):
		if debug:
			print_nxs(f"Result: ", color="yellow", nojump=True)
			print_nxs(result, color="dark_gray")

	arguments = parameter[1:]
	__main__.context_args = {}  # Conserve tous les paramètres au fil du flow

	for proc in data:
		result = None

		if 'path' in proc:
			mod_file = impmagic.get_from_file(join(flow_fabric, proc['path']))
			func = getattr(mod_file, proc['func_name'])

			if verbose:
				logs(f"Démarrage de la fonction {proc['func_name']}", "info")

			if len(proc['arguments']):
				try:
					args_function = parse_arguments(proc['arguments'], arguments)
				except ValueError as e:
					# Arguments obligatoires manquants, demander à l'utilisateur
					missing_args = str(e).split(":")[-1].strip().split(",")
					for arg in missing_args:
						val = input(f"{arg.strip()}: ")
						arguments.append(val)
					args_function = parse_arguments(proc['arguments'], arguments)
				
				# Enregistrer les arguments utilisés
				__main__.context_args.update(args_function)

				result = func(**args_function)
				show_debug(result)

			else:
				result = func()
				show_debug(result)
		else:
			logs(f"flow {task_name}: path non identifié", "warning")

		# Préparer les arguments pour la fonction suivante
		if result:
			if isinstance(result, tuple):
				arguments = list(result)
			else:
				arguments = [result]
		else:
			arguments = []


@impmagic.loader(
	{'module':'app.logs', 'submodule': ['logs']},
	{'module':'os.path', 'submodule': ['abspath', 'join', 'split']},
	{'module':'core.sandbox.env', 'submodule': ['command_shell', 'install_pool']},
	{'module':'core.sandbox.sandbox', 'submodule': ['Sandbox']},
)
def run_func(task_type, task_name, task_data, parameter, flow_fabric, debug, is_sandbox=False, verbose=False, timer=False, identity=False):
	payload = {
		"type": task_type,
		"task_name": task_name,
		"data": task_data,
		"parameter": parameter,
		"flow_fabric": flow_fabric,
		"debug": debug,
		"timer": timer,
		"verbose": verbose,
		"identity": identity,
	}

	payload = json.dumps(payload)
	payload_based = base64.b64encode(payload.encode())

	runner_file = abspath(__file__)
	
	requirements = []
	for ops in task_data:
		if 'requirements' in ops:
			requirements = list(set(requirements + ops['requirements']))

	if is_sandbox:
		logs("Préparation de la sandbox")
		requirements = list(set(requirements + ['zpp_flow']))
		sand_env = Sandbox(requirements)
		env_exe = sand_env.context.env_exe
	else:
		env_exe = sys.executable
		if requirements:
			install_pool(env_exe, requirements, force=False)

	command_shell(env_exe, ["python", runner_file], args=[payload_based])


@impmagic.loader(
	{'module':'os'},
	{'module':'sys'},
	{'module':'time'},
	{'module':'pathlib', 'submodule':['Path']},
	{'module':'vault', 'submodule': ['get_password']},
)
def main():
	if len(sys.argv)>1:
		payload_debased = base64.b64decode(sys.argv[1].encode())
		payload = json.loads(payload_debased)

		# Chemin absolu du dossier à ajouter
		chemin = os.path.abspath(Path(__file__).resolve().parent.parent)
		if chemin not in sys.path:
			sys.path.insert(0, chemin)

		if payload['timer']:
			start_time = time.time()

		if payload['identity']:
			#Récupération d'une clé pour ouvrir le vault dans __main__ avec le keyring
			get_password(get_key_from_keyring=True)




		if payload['type']=="task":
			run_task(task_name=payload['task_name'], data=payload['data'], parameter=payload['parameter'], flow_fabric=payload['flow_fabric'], debug=payload['debug'], verbose=payload['verbose'])
		else:
			run_flow(task_name=payload['task_name'], data=payload['data'], parameter=payload['parameter'], flow_fabric=payload['flow_fabric'], debug=payload['debug'], verbose=payload['verbose'])

		if payload['timer']:
			from app.logs import format_duration, print_nxs
			end_time = time.time()
			elapsed_time = end_time - start_time
			print_nxs(f"Temps écoulé pour {payload['task_name']} : {format_duration(elapsed_time)}")

if __name__ == '__main__':
	main()