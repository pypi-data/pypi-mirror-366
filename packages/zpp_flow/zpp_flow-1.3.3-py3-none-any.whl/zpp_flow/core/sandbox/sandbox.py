import impmagic
import __main__


class Sandbox:
	@impmagic.loader(
		{'module':'app.logs', 'submodule': ['logs']},
		{'module':'re', 'submodule': ['compile']},
		{'module':'core.sandbox.env', 'submodule': ['Context', 'create_temp_env', 'install_pool', 'open_environment']},
		{'module':'core.sandbox.package', 'submodule': ['get_all_package', 'package_regex']},
	)
	def __init__(self, requirements=None):
		name, pathenv = create_temp_env(upgradepip=False)
		self.context = Context(pathenv, name)

		if requirements:
			logs("Installation des dépendances")
			deps = []
			for package in requirements:
				package_compiled = compile(package_regex)
				package_match = package_compiled.search(package)
				if package_match!=None:
					deps.append(package)

			if len(deps):
				install_pool(self.context.env_exe, deps, force=True)

			"""
			deps = get_all_package(context.env_exe)
			for name, version in deps.items():
				print(f"{name}=={version}")
			"""

	@impmagic.loader(
		{'module':'core.sandbox.env', 'submodule': ['command_shell']},
	)
	def run(self, command):
		logs("Lancement du script")
		command_shell(self.context.env_exe, command, args=None, timer=False)
		#open_environment(pathenv)
