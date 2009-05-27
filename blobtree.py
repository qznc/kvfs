# -!- encoding: utf8 -!-

from hashlib import md5
import os

_DATATYPE = "d"
_TREETYPE = "t"

def hashed(data):
	return md5(data).hexdigest()

class DataBlob:
	def __init__(self, data):
		self.data = str(data)
		self.id = hashed(data)
	def __str__(self):
		return _DATATYPE+":%i:%s" % (len(self.data), self.data)

class TreeBlob:
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
		assert not os.path.sep in name
		blob = DataBlob(data)
		self.contents[name] = (blob.id,meta)
		return blob
	def insert(self, name, id, meta):
		assert not os.path.sep in name
		self.contents[name] = (id,meta)
	def resolve(self, path):
		"""returns (unresolved rest path, blob id, blob meta info)"""
		rest_path = ""
		if os.path.sep in path:
			i = path.index(os.path.sep)
			name = path[:i]
			rest_path = path[i+len(os.path.sep):]
			id, meta = self.contents[path]
		else:
			id, meta = self.contents[path]
		return rest_path, id, meta
	def get_meta(self, name):
		id, meta = self.contents[name]
		return meta
	def get_id(self):
		return hashed(str(self))
	id = property(get_id)

def parse_dir(data):
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
	return TreeBlob(contents)

def parse_data(data):
	assert data.startswith(_DATATYPE)
	data = data[len(_DATATYPE)+1:]
	length = int(data[:data.index(':')])
	skip = len(str(length))+1
	return DataBlob(data[skip:skip+length])

def parse(data):
	if data.startswith(_DATATYPE):
		return parse_data(data)
	if data.startswith(_TREETYPE):
		return parse_dir(data)
	raise Exception("unknown data: "+data)
	

class BlobTree:
	ROOT = 'root'
	def __init__(self, kv_store):
		self._kv = kv_store
		if not self.ROOT in kv_store:
			root = TreeBlob()
			kv_store[root.id] = str(root)
			kv_store[self.ROOT] = root.id
	def create_data(self, path, meta):
		end_blob = DataBlob("")
		self._kv[end_blob.id] = str(end_blob)
		self._save_path(path, end_blob, meta)
		return end_blob
	def _get_root_blob(self):
		return parse(self._kv[self._kv[self.ROOT]])
	def _get_blob_line(self, path):
		if not path:
			return [self._get_root_blob()]
		assert path.startswith(os.path.sep)
		path = path[len(os.path.sep):]
		current = self._get_root_blob()
		line = [current]
		path, id, meta = current.resolve(path)
		while path:
			current = parse(self._kv[id])
			line.append(current)
			path, id, meta = current.resolve(path)
		line.append(parse(self._kv[id]))
		return line
	def set_data(self, path, data):
		new_blob = DataBlob(data)
		self._kv[new_blob.id] = str(new_blob)
		self._save_path(path, new_blob)
	def _save_path(self, path, new_blob, meta=None):
		path = path.split(os.sep)
		blob_line = self._get_blob_line(os.sep.join(path[:-1]))
		assert len(path) == len(blob_line)+1, str(path)+" vs "+str(blob_line)
		for i in xrange(len(blob_line)):
			name = path.pop()
			blob = blob_line.pop()
			blob.insert(name, new_blob.id, meta)
			self._kv[blob.id] = str(blob)
			new_blob = blob
		self._kv[self.ROOT] = new_blob.id
	def get_data(self, path):
		blob_line = self._get_blob_line(path)
		if not isinstance(blob_line[-1], DataBlob):
			print blob_line
			raise Exception("not a data object")
		return blob_line[-1].data
	def get_meta_data(self, path):
		blob_line = self._get_blob_line(path)
		dir = blob_line[-2]
		name = os.path.basename(path)
		return dir.get_meta(name)
	def __str__(self):
		return str(self._kv)




if __name__ == "__main__":
	msg = "Hello Wörld! How are you?"
	meta_msg = "Söme meta data"
	T = BlobTree(dict())
	T.create_data("/blub", meta_msg)
	T.set_data("/blub", msg)
	T.create_data("/second", "more meta data")
	print T.get_meta_data("/second")
	assert msg == T.get_data("/blub")
	print T

