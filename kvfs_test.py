from kvfs import KVFS
import stat

def test_basic():
	K = KVFS(dict())
	K.getattr("/")
	K.readdir("/")

def test_basic_file():
	K = KVFS(dict())
	K.create("/blub")
	K.getattr("/blub")
	K.remove("/blub")
	K.flush()

def test_basic_dir():
	K = KVFS(dict())
	K.mkdir("/bla")
	K.getattr("/bla")
	K.readdir("/bla")
	K.remove("/bla")
	K.flush("/")

def test_root():
	K = KVFS(dict())
	K.getattr("/")
	K.mkdir("/bla")
	K.remove("/bla")
	K.getattr("/")

