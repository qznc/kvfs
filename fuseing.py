class FuseFile:
	def __init__(self, fs):
		self._fs = fs

	# init operations (open, create)
	def open(self, path, flags):
		"""open a file"""
		pass

	def create(self, path, mode):
		"""create a file"""
		pass

	# proxy operations 
	# (read, write, fsync, release, flush, fgetattr, ftruncate, lock)
	def read(self, path, length, offset, fh=None):
		"""read data from a file"""
		pass

	def write(self, path, buf, offset, fh=None):
		"""write data to a file"""
		pass

	def fsync(self, path, fdatasync, fh=None):
		pass

	def release(self, path, fh=None):
		pass

	def flush(self, path, fh=None):
		"""clear all buffers, finish all pending operations"""
		pass

	def fgetattr(path, fh=None):
		pass

	def ftruncate(self, path, len, fh=None):
		pass

	def lock(self):
		pass

class FuseDir:
	def __init__(self, fs):
		self._fs = fs

	# init operation
	def opendir(self):
		pass

	# proxy operation (readdir, fsyncdir, releasedir)
	def readdir(self):
		pass

	def fsyncdir(self):
		pass

	def releasedir(self):
		pass


if __name__ == "__main__":
	from kvfs import KVFS
	core = KVFS(dict())

	import fuse, sys
	if len(sys.argv) != 2:
		print 'usage: %s <mountpoint>' % sys.argv[0]
		sys.exit(1)
	fuse.fuse_python_api = (0, 2)
	fs = fuse.Fuse()
	fs.parse(sys.argv)
	fs.file_class = FuseFile(core)
	fs.dir_class = FuseDir(core)
	fs.main()
