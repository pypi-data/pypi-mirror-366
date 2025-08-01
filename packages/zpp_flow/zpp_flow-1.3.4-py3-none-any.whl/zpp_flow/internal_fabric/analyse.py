import impmagic

def merge_dicts(default_dict, custom_dict):
    result = default_dict.copy()

    for key, value in custom_dict.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                # Fusion récursive des dictionnaires imbriqués
                result[key] = merge_dicts(result[key], value)

            elif isinstance(result[key], list) and isinstance(value, list):
                # Concaténation des listes
                result[key] += value

                # Tri par 'order' si applicable
                if result[key] and isinstance(result[key][0], dict) and 'order' in result[key][0]:
                    result[key] = sorted(result[key], key=lambda x: x.get('order', 0))

            else:
                # Écrasement simple si types différents ou pas gérés
                result[key] = value
        else:
            result[key] = value

    return result


#Vérifie si une fonction attends des arguments
@impmagic.loader(
	{'module':'inspect'}
)
def get_function_arguments(func):
	# Obtenir les arguments de la fonction
	signature = inspect.signature(func)
	parameters = signature.parameters
	
	# Créer des listes pour différents types d'arguments
	arguments = []
	args = False
	kwargs = False
	kwonlyargs = []
	
	# Classer les arguments en fonction de leur type
	for name, param in parameters.items():
		if param.kind == inspect.Parameter.VAR_POSITIONAL:
			args = True
		elif param.kind == inspect.Parameter.VAR_KEYWORD:
			kwargs = True
		elif param.default == inspect.Parameter.empty:
			arguments.append((name, ))
		else:
			arguments.append((name, param.default))
	
	return {
		'arguments': arguments,
		'args': args,
		'kwargs': kwargs,
	}


#Récupération des informations d'une fonction
def get_function_info(mod_file, data, type):
	content = []
	for func_name, decorators_list in data.items():  # data est dict func_name -> list
		for dec in decorators_list:
			insert_fabric = {'func_name': func_name}
			custom = {}

			func_inf = getattr(mod_file, func_name, None)

			if callable(func_inf):
				# Récupérer tous les attributs de la fonction
				attributes = dir(func_inf)
				
				# Filtrer les attributs qui commencent par '_taskflow'
				flow_attributes = [attr for attr in attributes if attr.startswith('_taskflow_')]
				for attribute in flow_attributes:
					custom[attribute[10:]] = getattr(func_inf, attribute, None)

				#Parse des decorators pour récupérer les fonctions nécessaires
				if "decorators" in custom:
					for i, d in enumerate(custom['decorators'].copy()):
						# Ici on ignore, car on prend direct 'dec' en paramètre

						pass  # On peut virer cette boucle, on a 'dec' dans le paramètre externe

				insert = insert_fabric.copy()
				#Définition du nom
				if 'name' not in insert:
					insert['name'] = func_name
				
				args_type = get_function_arguments(func_inf)
				insert.update(args_type)
				insert.update(dec)

				if f'is_{type}' in insert and insert[f'is_{type}']:
					content.append(insert)

	return content


@impmagic.loader(
	{'module':'os'}
)
def parse_module(mod_file, flow_fabric=None):
	func_total = {'task': {}, 'flow': {}}

	mod_name = mod_file.__name__

	mod_filename = mod_file.__file__
	if flow_fabric:
		mod_filename = mod_filename.replace(flow_fabric + os.sep, "")

	task_funcs, flow_funcs = find_decorated_functions(mod_file)
	task_data = get_function_info(mod_file, task_funcs, type="task")
	flow_data = get_function_info(mod_file, flow_funcs, type="flow")

	for element in (task_data + flow_data):
		if element.get('is_task'):
			type_task = 'task'
		else:
			type_task = 'flow'

		element['path'] = mod_filename

		element_name = element.get('name')
		if not element_name:
			raise ValueError("Element missing 'name' key")

		# On peut supprimer 'name' si tu veux éviter duplication,
		# mais prudence : ne pas l'utiliser ensuite !
		del element['name']

		if element_name not in func_total[type_task]:
			func_total[type_task][element_name] = [element]
		else:
			# Vérifie la présence d'ordre pour tri
			if 'order' in func_total[type_task][element_name][0] and 'order' in element:
				func_total[type_task][element_name].append(element)
				func_total[type_task][element_name] = sorted(func_total[type_task][element_name], key=lambda x: x['order'])
			else:
				raise ValueError(f"Value 'order' not defined for multi-task '{element_name}'")

	return func_total



@impmagic.loader(
	{'module':'internal_fabric.fabric', 'submodule': ['tree_fabric']}
)
def tree_plugin(flow_fabric):
	mod_data = {}

	fabric_file = tree_fabric(flow_fabric)

	for file in fabric_file:
		mod_file = impmagic.get_from_file(file)

		if mod_file:
			mod_data_file = parse_module(mod_file, flow_fabric=flow_fabric)
			mod_data = merge_dicts(mod_data_file, mod_data)

	#Ajout des fonctions *
	if mod_data:
		if '*'in mod_data['task']:
			mod_data['task'] = broadcast_function(mod_data['task'], mod_data['task']['*'])
			
		if '*'in mod_data['flow']:
			mod_data['flow'] = broadcast_function(mod_data['flow'], mod_data['flow']['*'])

	return mod_data


@impmagic.loader(
	{'module':'inspect'}
)
def find_decorated_functions(module):
    task_funcs = {}
    flow_funcs = {}

    for name, func in inspect.getmembers(module, inspect.isfunction):
        decorators = getattr(func, '_taskflow_decorators', [])
        if decorators:
            # Filtrer les décorateurs tasks et flows séparément
            task_decos = [d for d in decorators if d.get('is_task')]
            flow_decos = [d for d in decorators if d.get('is_flow')]

            if task_decos:
                task_funcs[name] = task_decos
            if flow_decos:
                flow_funcs[name] = flow_decos

    return task_funcs, flow_funcs


#Ajouter les fonctions * aux autres fonctions
def broadcast_function(mod_data, function):
	del mod_data['*']

	for task_name, task in mod_data.items():
		mod_data[task_name] = task + function
		mod_data[task_name] = sorted(mod_data[task_name], key=lambda x: x['order'])

	return mod_data