from hashlib import md5
import os

def hashed(data):
	return md5(data).hexdigest()

class DataBlob:
	type = "blob"
	def __init__(self, data):
		self.data = data
		self.id = hashed(data)
	def __str__(self):
		return "data:%i:%s:%s" % (len(self.data), self.id, self.data)

class TreeBlob:
	type = "dir"
	def __init__(self, contents):
		self.contents = contents
	def __str__(self):
		lst = list()
		print "contents", self.contents
		for name, blob, meta in self.contents:
			s = "%s:%s:%s" % (name, blob.id, meta)
			lst.append("%i:%s" % (len(s), s))
		return "dir:"+';'.join(lst)
	def add(self, name, blob, meta):
		self.contents.append(name, blob.id, meta)
	def resolve(self, name):
		for n, blob, meta in self.contents:
			if n == name:
				return blob
		return None

def parse_dir(data):
	assert data.startswith("dir:")
	data = data[4:]
	data = data.split(';')
	for d in data:
		print d
	print "parsed", data
	return TreeBlob(data)

def parse(data):
	if data.startswith("data:"):
		return parse_data(data)
	if data.startswith("dir:"):
		return parse_dir(data)
	raise Exception("unknown data: "+data)
	

class BlobTree:
	ROOT = ''
	def __init__(self, kv_store):
		self._kv = kv_store
		if not self.ROOT in kv_store:
			kv_store[self.ROOT] = str(TreeBlob([]))
	def create_data(self, path):
		path = path.split(os.sep)
		blob = DataBlob("")
		return blob
	def set_data(self, path, data):
		print "path:", path
		path = path.split(os.sep)
		print "path:", path
		dir = os.sep.join(path[:-1])
		name = path[-1]
		print "dir",dir
		dir = self.get_blob(dir)
		print "dir",dir
		new_blob = DataBlob(data)
		meta = ""
		dir.add(name, new_blob, meta)
		return new_blob
	def get_blob(self, path):
		print "path:", path
		path = path.split(os.sep)
		print "path:", path
		blob = parse(self._kv[path[0]])
		for p in path[1:]:
			if blob.type == "file":
				return blob
			else:
				blob = blob.resolve(p)
		return blob
	def __str__(self):
		return str(self._kv)




if __name__ == "__main__":
	T = BlobTree(dict())
	print T
	print T.create_data("/blub")
	print T.set_data("/blub", "hello world!")

