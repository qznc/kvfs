from blobtree import BlobTree
import errno
import cPickle as pickle
import stat
import time
import os

class _MetaData(dict):
	"""A dict that serializes to a pickled string"""
	def __init__(self, data=None):
		dict.__init__(self)
		if data:
			# load pickled data
			for key, val in pickle.loads(data).items():
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
		return pickle.dumps(self)

def _raise_io(number, path=None):
	# behave according to Fuse
	msg = os.strerror(number)
	if path:
		msg = path+": "+msg
	err = IOError(msg)
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
		except KeyError:
			_raise_io(errno.ENOENT, path)
			
	def setattr(self, path, attr):
		"""Sets the attributes of the object at `path`."""
		if path == "/":
			_raise_io(errno.EPERM, path)
		try:
			self._bt.set_meta_data(path, attr)
		except (KeyError, IndexError):
			_raise_io(errno.ENOENT, path)

	def create(self, path):
		"""create a file"""
		if self._bt.exists(path):
			_raise_io(errno.EEXIST, path)
		m = _MetaData()
		m['st_mode'] = m['st_mode'] | stat.S_IFREG
		m['st_size'] = 0
		self._bt.create_data(path, str(m))

	def mkdir(self, path):
		"""creates a directory"""
		if self._bt.exists(path):
			_raise_io(errno.EEXIST, path)
		m = _MetaData()
		m['st_mode'] = m['st_mode'] | stat.S_IFDIR
		self._bt.create_subtree(path, str(m))

	def readdir(self, path):
		"""read contents of a directory"""
		try:
			files = self._bt.list_dir(path)
		except KeyError:
			_raise_io(errno.ENOENT, path)
		yield '.'
		yield '..'
		for f in files:
			yield f

	def readlink(self, path):
		"""Resolves a symbolic link"""
		meta = self.getattr(path)
		try:
			return meta['symlink']
		except KeyError:
			_raise_io(errno.ENOLINK, path)

	def symlink(self, target, name):
		"""create a symbolic link target->name"""
		if self._bt.exists(target):
			_raise_io(errno.EEXIST, target)
		m = _MetaData()
		# use attributes to save target and link property
		m['symlink'] = name
		m['st_mode'] = m['st_mode'] | stat.S_IFLNK
		self._bt.create_data(target, str(m))
		
	def remove(self, path):
		"""removes a file or directory"""
		try:
			self._bt.unlink(path)
		except KeyError:
			_raise_io(errno.ENOENT, path)

	def rename(self, old, new):
		"""rename a file (note that directories may change)"""
		try:
			self._bt.rename(old, new)
		except KeyError:
			_raise_io(errno.ENOENT, old)

	def link(self, target, name):
		"""create a hardlink"""
		self._bt.create_data(target, self.getattr(name))
		self._bt.set_data(target, self._bt.get_data(name))
		# FIXME this is a copy, not a hardlink!
		# Subsequent changes won't be applied.
		# A transparent link blob type would be needed,
		# but that should rather be called a symlink.

	def _get_data(self, path):
		"""get data from path or raise IOERROR"""
		try:
			return self._bt.get_data(path)
		except KeyError:
			_raise_io(errno.ENOENT, path)
		except TypeError:
			_raise_io(errno.EISDIR, path)

	def read(self, path, length=2000000000, offset=0):
		"""read data from a file"""
		data = self._get_data(path)
		return data[offset:offset+length]

	def write(self, path, buf, offset=0):
		"""write data to a file"""
		meta = self.getattr(path)
		if offset==0 and len(buf) >= meta['st_size']:
			data = buf
		else:
			data = self._get_data(path)
			data = data[:offset] + buf + data[offset+len(buf):]
		meta['st_mtime'] = time.time()
		meta['st_size'] = len(data)
		self._bt.set_data(path, data, str(meta))

	def flush(self, path="/"):
		"""clear all buffers, finish all pending operations"""
		self._bt.flush()

	def truncate(self, path, length):
		"""truncate file to given length"""
		data = self._get_data(path)
		self._bt.set_data(path, data[:length])
