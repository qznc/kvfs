import fuse, stat
fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
	def __init__(self):
		self.st_mode = stat.S_IFDIR | 0755
		self.st_ino = 0
		self.st_dev = 0
		self.st_nlink = 2
		self.st_uid = 0
		self.st_gid = 0
		self.st_size = 4096
		self.st_atime = 0
		self.st_mtime = 0
		self.st_ctime = 0


class MyFuseFS(fuse.Fuse):
	def __init__(self, fs):
		print "my fuse fs initialized"
		fuse.Fuse.__init__(self)
		self._fs = fs

	def read(self, path, length, offset, fh=None):
		"""read data from a file"""
		pass

	def write(self, path, buf, offset, fh=None):
		"""write data to a file"""
		pass

	def readdir(self, path, offset, fh=None):
		print "readdir", path, offset
		for file in self._fs.get_directory(path):
			yield fuse.Direntry(file)

	def getattr(self, path):
		return MyStat()

	def mknod(self, path, attrs):
		pass

	def mkdir(self, path):
		pass

	def readlink(self, path):
		pass

	def unlink(self, path):
		pass

	def rmdir(self, path):
		pass

	def symlink(self, path, target):
		pass

	def rename(self, path, new):
		pass

	def link(self, path, target):
		pass

	def chmod(self, path, mod):
		pass

	def chown(self, path, owner):
		pass

	def truncate(self, path, length):
		pass

	def statfs(self, path):
		pass

	def getxattr(self, path, attr, rest):
		print "getxattr rest:", rest

	def listxattr(self, path):
		pass

	def setxattr(self, path, attr, value):
		pass

	def removexattr(self, path, attr):
		pass

	def utimens(self, path, ts_acc, ts_mod):
		pass

	def bmap(self, path):
		pass

	### optional methods

	def open(self, path, flags):
		"""open a file"""
		pass

	def create(self, path, mode):
		"""create a file"""
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
		"""truncate file at position len"""
		pass

	def lock(self):
		pass

	def opendir(self, path, fh=None):
		"""open a directory"""
		# optional
		# may return a file handle
		pass

	def fsyncdir(self, path, fh=None):
		# optional
		# fh may origin from opendir call
		pass

	def releasedir(self, path):
		print "release dir", path
		pass

	def access(self, path):
		pass

	def fsinit(self):
		"""start file system"""
		pass

	def fsdestroy(self):
		"""stop file system"""
		pass



if __name__ == "__main__":
	from kvfs import KVFS
	core = KVFS(dict())

	import sys
	if len(sys.argv) < 2:
		print 'usage: %s <mountpoint> [fuse options]' % sys.argv[0]
		sys.exit(1)
	fs = MyFuseFS(core)
	fs.parse(sys.argv)
	fs.main()
