from kvfs import KVFS
import stat

def test_basic():
	K = KVFS(dict())
	K.getattr("/")
	K.readdir("/")

def test_basic_file():
	K = KVFS(dict())
	K.create("/blub")
	attr = K.getattr("/blub")
	assert stat.S_ISREG(attr['st_mode'])
	K.remove("/blub")
	K.flush()

def test_basic_dir():
	K = KVFS(dict())
	K.mkdir("/bla")
	attr = K.getattr("/bla")
	assert stat.S_ISDIR(attr['st_mode'])
	dir = list(K.readdir("/bla"))
	assert '.' in dir
	assert '..' in dir
	K.remove("/bla")
	K.flush("/")

def test_root():
	K = KVFS(dict())
	attr = K.getattr("/")
	assert stat.S_ISDIR(attr['st_mode'])
	K.mkdir("/bla")
	K.remove("/bla")
	K.getattr("/")

