import fuse, stat
fuse.fuse_python_api = (0, 2)

class MyFuseFS(fuse.Fuse):
	def __init__(self, fs):
		print "my fuse fs initialized"
		fuse.Fuse.__init__(self)
		self._fs = fs
	
	def read(self, path, length, offset, fh=None):
		"""read data from a file"""
		return self._fs.read(path, length, offset)

	def write(self, path, buf, offset, fh=None):
		"""write data to a file, return amount of bytes written"""
		return self._fs.write(path, buf, offset)

	def readdir(self, path, offset, fh=None):
		return self._fs.readdir(path)

	def getattr(self, path):
		return self._fs.getattr(path)

	def rmdir(self, path):
		self._fs.rmdir(path)

	def create(self, path, mode, dev):
		"""create a file"""
		return self._fs.create(path, mode, dev)

	def fsinit(self):
		"""start file system"""
		print "fsinit"
		self.__getattr__ = self.__getattr

	def fsdestroy(self):
		"""stop file system"""
		print "fsdestroy"
		del self.__getattr__

	def __getattr(self, attr):
		print "fuse fs proxies", attr
		return getattr(self._fs, attr)

if __name__ == "__main__":
	from kvfs import KVFS
	kv = dict()
	core = KVFS(kv)

	import sys
	if len(sys.argv) < 2:
		print 'usage: %s <mountpoint> [fuse options]' % sys.argv[0]
		sys.exit(1)
	fs = MyFuseFS(core)
	fs.parse(sys.argv)
	fs.main()
	print kv
