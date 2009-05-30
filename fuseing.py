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
		for file in self._fs.readdir(path):
			yield fuse.Direntry(file)

	def getattr(self, path):
		print "getattr", path
		context = self.GetContext()
		attr = self._fs.getattr(path)
		attr['st_uid'] = context['st_uid']
		attr['st_gid'] = context['st_gid']
		return attr

	def fgetattr(self, path, fh=None):
		print "fgetattr", path
		return self._fs.getattr(path)

	def mkdir(self, path, mode):
		print "mkdir", path, oct(mode)
		return self._fs.mkdir(path)

	def rmdir(self, path):
		print "rmdir", path
		return self._fs.remove(path)

	def unlink(self, path):
		print "unlink", path
		return self._fs.remove(path)

	def create(self, path, mode, dev):
		"""create a file"""
		print "create", path, oct(mode), dev
		return self._fs.create(path, mode)

	def mknod(self, path, mode, dev):
		"""create a file"""
		print "mknod", path, oct(mode), dev
		return self._fs.create(path)

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
