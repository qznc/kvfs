import fuse 
fuse.fuse_python_api = (0, 2)

class MyFuseFS(fuse.Fuse):
	"""Implement a Fuse file system on top of KVFS
	
	additional functionality includes (pathetic) support for uid, gui attributes"""
	def __init__(self, fs):
		"""initialize with a dict for KVFS"""
		print "my fuse fs initialized"
		fuse.Fuse.__init__(self)
		self._fs = fs
	
	def read(self, path, length, offset, fh=None):
		"""read data from a file"""
		print "read", path
		return self._fs.read(path, length, offset)

	def write(self, path, buf, offset, fh=None):
		"""write data to a file, return amount of bytes written"""
		print "write", path
		self._fs.write(path, buf, offset)
		return len(buf)

	def readdir(self, path, offset, fh=None):
		"""return a list of directory entries in `path`"""
		for file in self._fs.readdir(path):
			yield fuse.Direntry(file)

	def getattr(self, path):
		"""return attribute 'struct' for object at `path`"""
		print "getattr", path
		context = self.GetContext()
		attr = self._fs.getattr(path)
		attr['st_uid'] = context['uid']
		attr['st_gid'] = context['gid']
		attr['st_ino'] = 0
		attr['st_dev'] = 0
		attr['st_nlink'] = 0
		attr['st_rdev'] = 0
		attr['st_blksize'] = 4096
		attr['st_blocks'] = 1
		return attr

	def fgetattr(self, path, fh=None):
		print "fgetattr", path
		return self.getattr(path)

	def mkdir(self, path, mode):
		"""create a directory"""
		print "mkdir", path, oct(mode)
		return self._fs.mkdir(path)

	def rmdir(self, path):
		"""remove a directory"""
		print "rmdir", path
		return self._fs.remove(path)

	def unlink(self, path):
		"""remove a file"""
		print "unlink", path
		return self._fs.remove(path)

	def create(self, path, mode, dev):
		"""create a file"""
		print "create", path, oct(mode), dev
		return self._fs.create(path)

	def mknod(self, path, mode, dev):
		"""create a file/device node/..."""
		print "mknod", path, oct(mode), dev
		return self._fs.create(path)

	def rename(self, source, target):
		print "rename", source, target
		self._fs.rename(source, target)

	def utime(self, path, time):
		print "utime", path, time

	def utimens(self, path, atime, mtime):
		print "utimens", path
		attr = self._fs.getattr(path)
		attr['st_mtime'] = mtime.tv_sec
		attr['st_atime'] = atime.tv_sec
		self._fs.setattr(path, attr)

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
	from scalaris_dict import scalaris_dict
	kv = scalaris_dict("http://localhost:8000/jsonrpc.yaws")
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
