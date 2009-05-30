from kvfs import KVFS
import stat

def test_basic_root():
	"""testing basic root properties"""
	K = KVFS(dict())
	attr = K.getattr("/")
	assert stat.S_ISDIR(attr['st_mode'])
	dir = K.readdir("/")
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
	K.flush("/")

def test_used_root():
	K = KVFS(dict())
	attr = K.getattr("/")
	assert stat.S_ISDIR(attr['st_mode'])
	K.mkdir("/bla")
	K.remove("/bla")
	K.getattr("/")

