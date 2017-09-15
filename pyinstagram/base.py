# -*- coding: utf-8 -*-
import requests

class InstagramClient(object):
	"""
	Classe principale della libreria!
	"""
	def __init__(self, access_token=None):
		self.access_token = access_token
		if not self.access_token:
			# TODO: Gestire il caso in cui l'access token scada
			raise Exception("Per usare la libreria devi prima autenticarti!")

	def get_media_recent(self, id=None):
		id = id or "self"
		res = requests.get("https://api.instagram.com/v1/users/{0}/media/recent/?access_token={1}".format(id, self.access_token))
		try:
			return res.json()
		except Exception:
			raise Exception(res.text)