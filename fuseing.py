import fuse 
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
		print "getattr", path
		return self._fs.getattr(path)

	def fgetattr(self, path, fh=None):
		print "fgetattr", path
		return self._fs.getattr(path)

	def mkdir(self, path, mode):
		context = self.GetContext()
		print "mkdir", path, oct(mode)
		return self._fs.mkdir(path, mode, context['uid'], context['gid'])

	def rmdir(self, path):
		print "rmdir", path
		return self._fs.remove(path)

	def unlink(self, path):
		print "unlink", path
		return self._fs.remove(path)

	def create(self, path, mode, dev):
		"""create a file"""
		context = self.GetContext()
		print "create", path, oct(mode), dev
		return self._fs.create(path, mode, dev, context['uid'], context['gid'])

	def mknod(self, path, mode, dev):
		"""create a file"""
		print "mknod", path, oct(mode), dev
		return self._fs.create(path, mode, dev)

	def fsinit(self):
		"""start file system"""
		print "fsinit"

	def fsdestroy(self):
		"""stop file system"""
		print "fsdestroy"

	def flush(self, path, fh=None):
		print "flush", path

	def fsync(self, path, fdatasync, fh=None):
		print "fsync", path, fdatasync

	def ftruncate(self, path, len, fh=None):
		print "ftruncate", path, len

	def fsyncdir(self, path, fdatasync, fh=None):
		print "fsyncdir", path, fdatasync


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
