

class base_info:

	def __init__(self, name, title, desc, tags, urls, refs, dois):
		self.name = name
		self.title = title
		self.desc = desc
		self.tags = tags
		self.urls = urls
		self.refs = refs
		self.dois = dois

		# check the format of DOI
		for _doi in dois:
			if not _doi.startswith('10.'):
				raise Exception('wrong DOI (%s)' % _doi)

