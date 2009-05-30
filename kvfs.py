from blobtree import BlobTree
import errno
import marshal
import stat
import time

class _MetaData:
	def __init__(self, str=None):
		if str:
			self.data = marshal.loads(str)
		else:
			self.data = {
					"st_size": 4096,
					"st_atime": int(time.time()),
					"st_mtime": int(time.time()),
					"st_ctime": int(time.time()),
					}
	def __setitem__(self, attr, value):
		self.data[attr] = value
	def __getattr__(self, attr):
		return self.data[attr]
	def __getitem(self, attr):
		return self.data[attr]
	def __str__(self):
		return marshal.dumps(self.data)
	def __nonzero__(self):
		return True

def raise_io(number):
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
		self.root_meta = _MetaData()

	def get_directory(self, path):
		return self._bt.list_dir(path)

	def getattr(self, path):
		"""Returns the attributes of the object at `path`."""
		if path == "/":
			return self.root_meta
		try:
			return _MetaData(self._bt.get_meta_data(path))
		except (KeyError, IndexError):
			raise_io(errno.ENOENT)

	def setattr(self, path, meta):
		if path == "/":
			self.root_meta = meta
		try:
			self._bt.set_meta_data(path, meta)
		except (KeyError, IndexError):
			raise_io(errno.ENOENT)

	def getxattr(self, path):
		"""Returns the extended attributes of the object at path. 
		Extended attributes are attributes not stored in inodes."""
		pass

	def chmod(self, path, mode):
		pass

	def chown(self, path, uid, gid):
		pass

	def create(self, path):
		"""create a file"""
		# TODO error if already exists
		m = _MetaData()
		self._bt.create_data(path, str(m))

	def mkdir(self, path):
		"""creates a directory"""
		# TODO error if already exists
		m = _MetaData()
		self._bt.create_subtree(path, str(m))

	def readdir(self, path, fh=None):
		"""read contents of a directory"""
		try:
			files = self._bt.list_dir(path)
		except KeyError:
			raise_io(errno.ENOENT)
		yield '.'
		yield '..'
		for f in files:
			yield f

	def readlink(self, path):
		"""Resolves a symbolic link"""
		pass

	def open(self, path, flags):
		pass

	def remove(self, path):
		"""removes a file or directory"""
		self._bt.unlink(path)

	def symlink(self, target, name):
		"""create a symlink"""
		pass

	def rename(self, old, new):
		"""rename a file (not that directories may change)"""
		pass

	def link(self, target, name):
		"""create a hardlink"""
		pass

	def read(self, path, length, offset, fh=None):
		"""read data from a file"""
		data = self._bt.get_data(path)
		return data[offset:offset+length]

	def write(self, path, buf, offset, fh=None):
		"""write data to a file"""
		data = self._bt.get_data(path)
		data = data[:offset] + buf + data[offset+len(buf):]
		self._bt.set_data(path, data)
		return len(buf)

	def flush(self, path="/", fh=None):
		"""clear all buffers, finish all pending operations"""
		pass

	def release(self, path, fh=None):
		pass

	def truncate(self, path, length, fh=None):
		"""truncate file to given length"""
		pass

	def utimens(self, path, times=None):
		pass
