import impmagic

import os

if os.name=='nt':
	path_rep = ["\\","/"]
else:
	path_rep = ["/","\\"]

#Calcul du chemin d'un fichier
@impmagic.loader(
	{'module':'os.path', 'submodule':['isabs','abspath']}
)
def path_reg(arg):
	if isabs(arg):
		return arg
	return abspath(arg)

#Cherche le terminal (cmd,powershell,bash...) sur lequel est exécuté l'app
@impmagic.loader(
	{'module':'os'},
	{'module':'psutil'}
)
def get_os():
	if os.name=="nt":
		if "nxs" not in psutil.Process(os.getppid()).name():
			return psutil.Process(os.getppid()).name()
		else:
			return psutil.Process(psutil.Process(os.getppid()).ppid()).name()
	else:
		return os.popen(f'ps -p {os.getppid()} -o comm=').read().strip()
