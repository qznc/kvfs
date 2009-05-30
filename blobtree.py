#!/usr/bin/env python
# -!- encoding: utf8 -!-
"""
A BlobTree is a tree of str object with str meta data.
Elements can be identified via their path.
"""

import os, hashlib

_DATATYPE = "d"
_TREETYPE = "t"

def _hashed(data):
	"""hash a str object"""
	return hashlib.md5(data).hexdigest()

"""
Blobs have an id attribute of type str and 
can be serialized via str(blob).
They are save in a key-value store with
id as key and str(blob) as value.
"""

class _DataBlob:
	"""a data blob to be saved in a kv store"""
	def __init__(self, data):
		self.data = str(data)
		self.id = _hashed(data)
	def __str__(self):
		return _DATATYPE+":%i:%s" % (len(self.data), self.data)
	@classmethod
	def parse(Cls, data):
		assert data.startswith(_DATATYPE)
		data = data[len(_DATATYPE)+1:]
		length = int(data[:data.index(':')])
		skip = len(str(length))+1
		return Cls(data[skip:skip+length])

class _TreeBlob:
	"""a tree blob with children to be saved in a kv store"""
	def __init__(self, contents=None):
		self.contents = contents or dict()
	def __str__(self):
		lst = list()
		for name in self.contents:
			blob_id, meta = self.contents[name]
			s = "%s:%s:%s" % (name, blob_id, meta)
			lst.append("%i:%s" % (len(s), s))
		return _TREETYPE+":"+''.join(lst)
	def set(self, name, data, meta):
		"""insert a new data child"""
		assert not os.path.sep in name
		blob = _DataBlob(data)
		self.contents[name] = (blob.id,meta)
		return blob
	def insert(self, name, id, meta):
		"""insert an existing blob child by id"""
		assert not os.path.sep in name
		self.contents[name] = (id,meta)
	def unlink(self, name):
		del self.contents[name]
	def resolve(self, path):
		"""returns (unresolved rest path, blob id, blob meta info)"""
		rest_path = ""
		if os.path.sep in path:
			i = path.index(os.path.sep)
			name = path[:i]
			rest_path = path[i+len(os.path.sep):]
			id, meta = self.contents[name]
		else:
			id, meta = self.contents[path]
		return rest_path, id, meta
	def get_meta(self, name):
		"""get meta data of child"""
		id, meta = self.contents[name]
		return meta
	def set_meta(self, name, meta):
		"""overwrite meta data of child"""
		id, old_meta = self.contents[name]
		self.contents[name] = (id, meta)
	def list_childs(self):
		for name in self.contents.keys():
			yield name
	def _get_id(self):
		return _hashed(str(self))
	id = property(_get_id, doc="key for this directory state blob")
	@classmethod
	def parse(Cls, data):
		assert data.startswith(_TREETYPE)
		data = data[len(_TREETYPE)+1:]
		contents = dict()
		while data:
			length = int(data[:data.index(':')])
			skip = len(str(length))+1
			current = data[skip:skip+length]
			data = data[skip+length:]
			name,id,meta = current.split(':')
			contents[name] = (id,meta)
		return Cls(contents)

def _parse(data):
	"""parse a str object and return TreeBlob or DataBlob object"""
	if data.startswith(_DATATYPE):
		return _DataBlob.parse(data)
	if data.startswith(_TREETYPE):
		return _TreeBlob.parse(data)
	raise Exception("unknown data: "+data)
	

class BlobTree:
	"""implements a tree of str data with meta info
	and saves everything in a key-value store"""
	ROOT = 'root'
	def __init__(self, kv_store):
		self._kv = kv_store
		if not self.ROOT in kv_store:
			root = _TreeBlob()
			kv_store[root.id] = str(root)
			kv_store[self.ROOT] = root.id
	def create_data(self, path, meta):
		"""create a data object at path"""
		end_blob = _DataBlob("")
		self._kv[end_blob.id] = str(end_blob)
		self._save_path(path, end_blob, meta)
	def create_subtree(self, path, meta):
		"""create a tree object at path"""
		end_blob = _TreeBlob(dict())
		self._kv[end_blob.id] = str(end_blob)
		self._save_path(path, end_blob, meta)
	def _get_root_blob(self):
		"""get the root TreeBlob"""
		return _parse(self._kv[self._kv[self.ROOT]])
	def _get_blob_line(self, path):
		"""get a list of blobs representing the path"""
		if path.endswith(os.sep):
			path = path[:-len(os.sep)]
			# path may be '' now
		if not path:
			return [self._get_root_blob()]
		assert path.startswith(os.sep)
		path = path[len(os.sep):]
		current = self._get_root_blob()
		line = [current]
		path, id, meta = current.resolve(path)
		while path:
			current = _parse(self._kv[id])
			line.append(current)
			path, id, meta = current.resolve(path)
		line.append(_parse(self._kv[id]))
		return line
	def set_data(self, path, data):
		"""put data into data object at path"""
		new_blob = _DataBlob(data)
		self._kv[new_blob.id] = str(new_blob)
		self._save_path(path, new_blob)
	def _save_path(self, path, new_blob, meta=None):
		"""save new_blob at path by updating all TreeBlobs above"""
		assert path.startswith(os.sep)
		path = path.split(os.sep)
		blob_line = self._get_blob_line(os.sep.join(path[:-1]))
		assert len(path) == len(blob_line)+1, str(path)+" vs "+str(blob_line)
		for i in xrange(len(blob_line)):
			name = path.pop()
			blob = blob_line.pop()
			if name and not meta:
				meta = blob.get_meta(name)
			blob.insert(name, new_blob.id, meta)
			self._kv[blob.id] = str(blob)
			new_blob = blob
			meta = None # preserve meta data of upper levels
		self._kv[self.ROOT] = new_blob.id
	def get_data(self, path):
		"""return data from data object at path"""
		blob_line = self._get_blob_line(path)
		if not isinstance(blob_line[-1], _DataBlob):
			raise Exception("not a data object")
		return blob_line[-1].data
	def get_meta_data(self, path):
		"""return meta data from data object at path"""
		blob_line = self._get_blob_line(path)
		dir = blob_line[-2]
		name = os.path.basename(path)
		return dir.get_meta(name)
	def set_meta_data(self, path, meta):
		"""overwrite meta data"""
		blob_line = self._get_blob_line(path)
		dir = blob_line[-2]
		name = os.path.basename(path)
		dirname = os.path.dirname(path)
		dir.set_meta(name, meta)
		self._kv[dir.id] = str(dir)
		self._save_path(dirname, dir)
	def unlink(self, path):
		"""remove a path from the system"""
		blob_line = self._get_blob_line(path)
		dir = blob_line[-2]
		name = os.path.basename(path)
		dirname = os.path.dirname(path)
		print dirname
		dir.unlink(name)
		self._save_path(dirname, dir)
	def is_data(self, path):
		blob_line = self._get_blob_line(path)
		return isinstance(blob_line[-1], _DataBlob)
	def is_dir(self, path):
		blob_line = self._get_blob_line(path)
		return isinstance(blob_line[-1], _TreeBlob)
	def exists(self, path):
		try:
			blob_line = self._get_blob_line(path)
		except KeyError:
			return False
		return True
	def list_dir(self, path):
		blob_line = self._get_blob_line(path)
		return blob_line[-1].list_childs()
	def __str__(self):
		return "\n".join("%32s\t%s" % (k,v) for k,v in self._kv.items())

if __name__ == "__main__":
	msg = "Hello Wörld! How are you?"
	meta_msg = "Söme meta data"
	T = BlobTree(dict())
	T.create_data("/blub", meta_msg)
	T.set_data("/blub", msg)
	T.create_data("/second", "more meta data")
	T.create_data("/sub/blub", meta_msg)
	T.set_data("/sub/blub", "some data")
	print T

