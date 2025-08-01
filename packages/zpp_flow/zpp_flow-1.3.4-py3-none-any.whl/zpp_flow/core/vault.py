import os
import __main__
import zpp_store
import keyring

class Vault:
	def __init__(self, vault_file=None, get_key_from_keyring=False):
		if not vault_file:
			if os.name=="nt":
				vault_file = os.path.expanduser(os.path.join("~\\.config\\zpp_flow\\.vault", "flow.vault"))
			else:
				vault_file = os.path.expanduser(os.path.join("~/.config/zpp_flow/.vault", "flow.vault"))

		if get_key_from_keyring:
			password = keyring.get_password("flow", "identity")
			self.vault = zpp_store.Store(filename=vault_file, format= zpp_store.Formatstore.to_binary, protected=True, password=password)

		else:
			self.vault = zpp_store.Store(filename=vault_file, format= zpp_store.Formatstore.to_binary, protected=True)


	def set_password(self, component, password=None):
		try:
			if not password:
				passwd = zpp_store.secure_input("key: ")

			self.vault.push(component, passwd)
			return True
		except:
			return False


	def get_password(self, component=None):
		try:
			return self.vault.pull(component)
		except:
			return ""


	def unset_password(self, component=None):
		try:
			self.vault.erase(component)
			return True
		except:
			return False


	def get_list(self):
		return self.vault.list()


def get_password(component=None, get_key_from_keyring=False):
	if not hasattr(__main__, "vault"):
		__main__.vault = Vault(get_key_from_keyring=get_key_from_keyring)
	return __main__.vault.get_password(component)
