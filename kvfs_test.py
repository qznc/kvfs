# -!- encoding: utf-8 -!-
from kvfs import KVFS
import stat
import errno

def test_basic_root():
	"""testing basic root properties"""
	K = KVFS(dict())
	attr = K.getattr("/")
	assert stat.S_ISDIR(attr['st_mode'])
	dir = list(K.readdir("/"))
	assert len(dir) == 2
	assert '.' in dir
	assert '..' in dir

def test_basic_file():
	"""testing basic file properties"""
	K = KVFS(dict())
	K.create("/blub")
	assert "blub" in K.readdir("/")
	attr = K.getattr("/blub")
	assert stat.S_ISREG(attr['st_mode'])
	K.remove("/blub")
	print list(K.readdir("/"))
	assert not "blub" in K.readdir("/")
	K.flush()

def test_basic_dir():
	"""testing basic directory properties"""
	K = KVFS(dict())
	K.mkdir("/bla")
	assert "bla" in K.readdir("/")
	assert stat.S_ISDIR(K.getattr("/bla")['st_mode'])
	dir = list(K.readdir("/bla"))
	assert '.' in dir
	assert '..' in dir
	K.remove("/bla")
	assert not "bla" in K.readdir("/")
	K.flush("/")

def test_used_root():
	K = KVFS(dict())
	attr = K.getattr("/")
	assert stat.S_ISDIR(attr['st_mode'])
	K.mkdir("/bla")
	K.remove("/bla")
	K.getattr("/")

def test_dir_operations():
	K = KVFS(dict())
	assert stat.S_ISDIR(K.getattr("/")['st_mode'])
	K.mkdir("/bla")
	assert "bla" in K.readdir("/")
	K.create("/bla/blub")
	assert "blub" in K.readdir("/bla")
	assert stat.S_ISREG(K.getattr("/bla/blub")['st_mode'])
	K.remove("/bla")
	assert not "bla" in K.readdir("/")
	assert stat.S_ISDIR(K.getattr("/")['st_mode'])

def test_basic_readwrite():
	msg = "Hello Wörld!"
	K = KVFS(dict())
	K.create("/blub")
	K.write("/blub", msg, 0)
	msg2 = K.read("/blub", len(msg), 0)
	assert msg == msg2, (msg, msg2)

def test_hardlink():
	msg = "Hello Wörld!"
	K = KVFS(dict())
	K.create("/blub")
	K.write("/blub", msg)
	K.link("/bla", "/blub")
	# This doesn't work if 'write' and 'link' order is changed,
	# but that problem is a deeper one.
	msg2 = K.read("/bla", len(msg))	
	assert msg == msg2, (msg, msg2)
	
def test_rename():
	K = KVFS(dict())
	K.mkdir("/sub")
	K.rename("/sub", "/dir")
	assert "dir" in K.readdir("/")
	assert not "sub" in K.readdir("/")
	# and again with changing directory
	K.create("/dir/sub")
	assert "sub" in K.readdir("/dir")
	K.rename("/dir/sub", "/blub")
	assert "blub" in K.readdir("/")
	assert not "sub" in K.readdir("/dir")

def test_truncate():
	K = KVFS(dict())
	K.create("/blub")
	K.write("/blub", "hello world")
	K.truncate("/blub", 5)
	data = K.read("/blub", 10)
	assert data == "hello"
	
def test_attributes():
	K = KVFS(dict())
	K.create("/blub")
	attr = K.getattr("/blub")	
	assert not 'extended' in attr
	attr['extended'] = "grins"
	K.setattr("/blub", attr)
	attr = K.getattr("/blub")
	assert 'extended' in attr
	assert attr['extended'] == "grins"
	del attr['extended']
	K.setattr("/blub", attr)
	attr = K.getattr("/blub")
	assert not 'extended' in attr
	
def test_symlink():
	K = KVFS(dict())
	K.create("/blub")
	K.symlink("/bla", "/blub")	
	assert stat.S_ISLNK(K.getattr("/bla")['st_mode'])
	assert K.readlink("/bla") == "/blub"

def test_sizes():
	msg = "tis is äi dest mässätsch"
	K = KVFS(dict())
	K.create("/blub")
	attr = K.getattr("/blub")
	assert attr['st_size'] == 0, attr['st_size']
	K.write("/blub", msg)
	attr = K.getattr("/blub")
	assert attr['st_size'] == len(msg), (attr['st_size'], len(msg))
	
def raises_errno(number, errmsg):
	"""decorator to check for IOError with errno attribute"""
	def decorate(func):
		def test():
			try:
				func()
				assert False,errmsg
			except IOError, e:
				assert e.errno == number, str(e)+" is not errno "+str(number)
		return test
	return decorate

@raises_errno(errno.EEXIST, "creating existant file?!")
def test_double_create():
	K = KVFS(dict())
	K.create("/blub")
	K.create("/blub")

@raises_errno(errno.EEXIST, "creating existant directory?!")
def test_double_mkdir():
	K = KVFS(dict())
	K.mkdir("/blub")
	K.mkdir("/blub")
		
@raises_errno(errno.ENOENT, "attributes of non-existant file?!")
def test_noexists_getattr():
	K = KVFS(dict())
	K.getattr("/blub")
	
@raises_errno(errno.ENOENT, "set attributes of non-existant file?!")
def test_noexists_setattr():
	K = KVFS(dict())
	K.setattr("/blub", "meta")
	
@raises_errno(errno.ENOENT, "remove non-existant file?!")
def test_noexists_remove():
	K = KVFS(dict())
	K.remove("/blub")
	
@raises_errno(errno.ENOENT, "rename non-existant file?!")
def test_noexists_rename():
	K = KVFS(dict())
	K.rename("/blub", "/bla")
	
@raises_errno(errno.ENOENT, "writing to non-existant file?!")
def test_noexists_write():
	K = KVFS(dict())
	K.write("/blub", "bla bla")		

@raises_errno(errno.EISDIR, "writing to directory?!")
def test_dir_write():
	K = KVFS(dict())
	K.mkdir("/blub")
	K.write("/blub", "bla bla")	

@raises_errno(errno.EISDIR, "reading from directory?!")
def test_dirs_read():
	K = KVFS(dict())
	K.mkdir("/blub")
	K.read("/blub")

@raises_errno(errno.ENOENT, "reading from non-existant file?!")
def test_noexists_read():
	K = KVFS(dict())
	K.read("/blub")
	
@raises_errno(errno.ENOENT, "truncate non-existant file?!")
def test_noexists_truncate():
	K = KVFS(dict())
	K.truncate("/blub", 5)
	
@raises_errno(errno.ENOENT, "readlink of non-existant file?!")
def test_noexists_readlink():
	K = KVFS(dict())
	K.readlink("/blub")
	
@raises_errno(errno.ENOLINK, "readlink of regular file?!")
def test_regular_readlink():
	K = KVFS(dict())
	K.create("/blub")
	K.readlink("/blub")
	
@raises_errno(errno.EEXIST, "symlink mustn't overwrite")
def test_exists_symlink():
	K = KVFS(dict())
	K.create("/blub")
	K.create("/bla")
	K.symlink("/bla", "/blub")

if __name__ == "__main__":
	import nose
	nose.main()
	