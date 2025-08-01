import impmagic
import sys
from cli import Cli
import threading
import io

class ThreadLocalRedirector:
    def __init__(self):
        self._local = threading.local()
        self._local.stdout = None
        self._local.stderr = None

    def set_redirect(self, stdout, stderr):
        self._local.stdout = stdout
        self._local.stderr = stderr

    def write(self, message):
        if self._local.stdout:
            self._local.stdout.write(message)
        else:
            self._original_stdout.write(message)

    def flush(self):
        if self._local.stdout:
            self._local.stdout.flush()
        else:
            self._original_stdout.flush()

# Créer les wrappers pour stdout et stderr
stdout_redirector = ThreadLocalRedirector()
stderr_redirector = ThreadLocalRedirector()

# Sauvegarder les originales
stdout_redirector._original_stdout = sys.stdout
stderr_redirector._original_stderr = sys.stderr

sys.stdout = stdout_redirector
sys.stderr = stderr_redirector


class DataSpace(threading.Thread):
	def __init__(self, command):
		threading.Thread.__init__(self)
		self.command = command

	def run(self):
		self.captured_stdout = io.StringIO()
		self.captured_stderr = io.StringIO()

		stdout_redirector.set_redirect(self.captured_stdout, self.captured_stderr)
		try:
			inst = Cli(["flow"]+self.command)		
			inst.switch()
		finally:
			stdout_redirector.set_redirect(None, None)  # Rétablir stdout et stderr

	def get_output(self):
		return self.captured_stdout.getvalue()

	def get_errors(self):
		return self.captured_stderr.getvalue()


class Console:
	def __init__(self):
		self.process = []
		self.loop()

	@impmagic.loader(
		{'module':'app.logs', 'submodule': ['print_nxs']},
	)
	def loop(self):
		while True:
			print_nxs("\n    ________             \n   / ____/ /___ _      __\n  / /_  / / __ \\ | /| / /\n / __/ / / /_/ / |/ |/ / \n/_/   /_/\\____/|__/|__/  \n                         \n")
			print(">> ", end='')
			command = input("")

			if len(command):
				if command=="exit":
					exit()

				command = command.split(" ")

				if command[0]=='run':
					d = DataSpace(command)
					d.start()
					self.process.append((command[1], d))
					#self.process.append(p)
				elif command[0]=='bg':
					self.background(command)
				else:
					inst = Cli(["flow"]+command)
					inst.switch()


	def run_cli(self, command):
		inst = Cli(["flow"]+command)
		inst.switch()


	@impmagic.loader(
		{'module':'app.logs', 'submodule': ['print_nxs']},
	)
	def background(self, command):
		if len(command)>1:
			for element in self.process:
				if element[0]==command[1]:
					print("OUTPUT: ")
					print(element[1].get_output())
					print("ERROR: ")
					print(element[1].get_errors())
		else:
			for process in self.process:
				print_nxs(f"{process[0]} - ", nojump=True)
				if process[1].is_alive():
					print_nxs("running", color="green")
				else:
					print_nxs("stopped", color="red")