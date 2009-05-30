from blobtree import BlobTree
import errno
import marshal
import stat
import time

class _MetaData(dict):
	"""A dict that serialized to a marshalled string"""
	def __init__(self, marsh=None):
		dict.__init__(self)
		if marsh:
			# load marshalled data
			for key, val in marshal.loads(marsh).items():
				self[key] = val
		else:
			# initialize defaults
			self.update({
					"st_mode": 0700,
					"st_size": 4096,
					"st_atime": int(time.time()),
					"st_mtime": int(time.time()),
					"st_ctime": int(time.time()),
					})
	def __str__(self):
		return marshal.dumps(self)

def _raise_io(number):
	# behave according to Fuse
	err = IOError()
	err.errno = number
	raise err

class KVFS:
	"""A Key-Value-File-System
	This class is initialized with a key value store
	and implements a file system on top of it,
	providing methods like open, close, read, write, ..."""
	def __init__(self, kv_store):
		self._bt = BlobTree(kv_store)
		m = _MetaData()
		m['st_mode'] = m['st_mode'] | stat.S_IFDIR
		self.root_meta = m

	def getattr(self, path):
		"""Returns the attributes of the object at `path`."""
		if path == "/":
			return self.root_meta
		try:
			return _MetaData(self._bt.get_meta_data(path))
		except (KeyError, IndexError):
			_raise_io(errno.ENOENT)
			
	def setattr(self, path, attr):
		"""Sets the attributes of the object at `path`."""
		if path == "/":
			self.root_meta = attr
		try:
			print "path", path
			self._bt.set_meta_data(path, attr)
		except (KeyError, IndexError):
			_raise_io(errno.ENOENT)

	def create(self, path):
		"""create a file"""
		# TODO error if already exists
		m = _MetaData()
		m['st_mode'] = m['st_mode'] | stat.S_IFREG
		self._bt.create_data(path, str(m))

	def mkdir(self, path):
		"""creates a directory"""
		# TODO error if already exists
		m = _MetaData()
		m['st_mode'] = m['st_mode'] | stat.S_IFDIR
		self._bt.create_subtree(path, str(m))

	def readdir(self, path):
		"""read contents of a directory"""
		try:
			files = self._bt.list_dir(path)
		except KeyError:
			_raise_io(errno.ENOENT)
		yield '.'
		yield '..'
		for f in files:
			yield f

	def readlink(self, path):
		"""Resolves a symbolic link"""
		pass

	def symlink(self, target, name):
		"""create a symbolic link"""
		pass
		
	def remove(self, path):
		"""removes a file or directory"""
		self._bt.unlink(path)

	def rename(self, old, new):
		"""rename a file (note that directories may change)"""
		self._bt.rename(old, new)

	def link(self, target, name):
		"""create a hardlink"""
		self._bt.create_data(target, self._bt.get_meta_data(name))
		self._bt.set_data(target, self._bt.get_data(name))
		# FIXME this is a copy, not a hardlink!
		# Subsequent changes won't be applied.
		# A transparent link blob type would be needed,
		# but that should rather be called a symlink.

	def read(self, path, length, offset=0):
		"""read data from a file"""
		data = self._bt.get_data(path)
		return data[offset:offset+length]

	def write(self, path, buf, offset=0):
		"""write data to a file"""
		data = self._bt.get_data(path)
		meta = _MetaData(self._bt.get_meta_data(path))
		data = data[:offset] + buf + data[offset+len(buf):]
		meta['st_mtime'] = time.time()
		self._bt.set_data(path, data, str(meta))
		return len(buf)

	def flush(self, path="/"):
		"""clear all buffers, finish all pending operations"""
		self._bt.flush()

	def truncate(self, path, length):
		"""truncate file to given length"""
		data = self._bt.get_data(path)
		self._bt.set_data(path, data[:length])
