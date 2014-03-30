

import serv_base
import logging

class web_handler(serv_base.service_base):

	def task(self, path):
		import os, config

		logging.info('loading web path: ' + path)
		_f = os.path.join(config.get_at('general', 'web_path'), path)

		self.output_file(_f)

