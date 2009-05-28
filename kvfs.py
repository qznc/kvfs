from blobtree import BlobTree
import fuse
import marshal
import stat

class _MetaData:
	def __init__(self, str=None):
		if str:
			self.data = marshal.loads(str)
		else:
			self.data = {
					"st_mode": stat.S_IFDIR | 0755,
					"st_ino": 0,
					"st_dev": 0,
					"st_nlink": 2,
					"st_uid": 0,
					"st_gid": 0,
					"st_size": 4096,
					"st_atime": 0,
					"st_mtime": 0,
					"st_ctime": 0
					}
		self.__setattr__ = self.__setattr
	def __setattr(self, attr, value):
		self.data[attr] = value
	def __getattr__(self, attr):
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
			return self._bt.get_meta_data(path)
		except (KeyError, IndexError):
			raise_io(fuse.ENOENT)

	def setattr(self, path, meta):
		if path == "/":
			self.root_meta = meta
		try:
			self._bt.set_meta_data(path, meta)
		except (KeyError, IndexError):
			raise_io(fuse.ENOENT)

	def getxattr(self, path):
		"""Returns the extended attributes of the object at path. 
		Extended attributes are attributes not stored in inodes."""
		pass

	def chmod(self, path, mode):
		pass

	def chown(self, path, uid, gid):
		pass

	def create(self, path, mode, dev):
		"""create a file"""
		m = _MetaData()
		m.st_mode = mode
		m.st_dev = dev
		self._bt.create_data(path, m)

	def mkdir(self, path, mode):
		"""creates a directory"""
		self._bt.create_subtree(path)

	def readdir(self, path, fh=None):
		"""read contents of a directory"""
		try:
			files = self._bt.list_dir(path)
		except KeyError:
			raise_io(fuse.ENOENT)
		yield fuse.Direntry('.')
		yield fuse.Direntry('..')
		for f in files:
			yield fuse.Direntry(f)

	def readlink(self, path):
		"""Resolves a symbolic link"""
		pass

	def open(self, path, flags):
		pass

	def unlink(self, path):
		"""removes a file"""
		pass

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

	def flush(self, path, fh=None):
		"""clear all buffers, finish all pending operations"""
		pass

	def release(self, path, fh=None):
		pass

	def truncate(self, path, length, fh=None):
		"""truncate file to given length"""
		pass

	def utimens(self, path, times=None):
		pass
