
class KVFS:
	"""A Key-Value-File-System
	This class is initialized with a key value store
	and implements a file system on top of it,
	providing methods like open, close, read, write, ..."""
	def __init__(self, kv_store):
		self._kv = kv_store

	def get_directory(self, path):
		return ['.', '..', 'blub']

	def get_attribute(self, path):
		"""Returns the attributes of the object at `path`."""
		pass

	def getxattr(self, path):
		"""Returns the extended attributes of the object at path. 
		Extended attributes are attributes not stored in inodes."""
		pass

	def chmod(self, path, mode):
		pass

	def chown(self, path, uid, gid):
		pass

	def create(self, path, mode):
		"""create a file"""
		pass

	def mkdir(self, path, mode):
		"""creates a directory"""
		pass

	def readdir(self, path, fh):
		"""read contents of a directory"""
		pass

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
		pass

	def write(self, path, buf, offset, fh=None):
		"""write data to a file"""
		pass

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
