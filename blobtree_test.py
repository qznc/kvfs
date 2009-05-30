#!/usr/bin/env python
# -!- encoding: utf8 -!-

from blobtree import BlobTree

class strdict:
	"""a more restrictive dict to keep BlobTree honest"""
	def __init__(self):
		self.data = dict()
	def __contains__(self, key):
		assert isinstance(key, str), key
		return key in self.data
	def __delitem__(self, key):
		assert isinstance(key, str), key
		del self.data[key]
	def __getitem__(self, key):
		assert isinstance(key, str), key
		return self.data[key]
	def __setitem__(self, key, value):
		assert isinstance(key, str), key
		assert isinstance(value, str), value
		self.data[key] = value

def test_basic():
	msg = "Hello Wörld! How are you?"
	meta_msg = "Söme meta data"
	T = BlobTree(strdict())
	T.create_data("/blub", meta_msg)
	T.set_data("/blub", msg)
	T.create_data("/second", "more meta data")
	assert meta_msg == T.get_meta_data("/blub")
	assert msg == T.get_data("/blub")
	print T.create_subtree("/sub", meta_msg)
	T.create_data("/sub/blub", meta_msg)
	T.set_data("/sub/blub", "some data")
	assert meta_msg == T.get_meta_data("/sub/blub")

def test_meta_data():
	meta1 = "apple"
	meta2 = "microsoft"
	meta3 = "linux"
	T = BlobTree(strdict())
	T.create_subtree("/sub", meta1)
	T.create_subtree("/sub/sub", meta2)
	T.create_data("/sub/data", meta3)
	T.set_data("/sub/data", "some data")
	assert meta1 == T.get_meta_data("/sub")
	assert meta2 == T.get_meta_data("/sub/sub")
	assert meta3 == T.get_meta_data("/sub/data")

	T.set_meta_data("/sub/data", meta1)
	assert meta1 == T.get_meta_data("/sub/data")

def test_peeking():
	T = BlobTree(strdict())
	assert not T.exists("/dummy")

def test_checking():
	T = BlobTree(strdict())
	T.create_subtree("/sub", "meta")
	T.create_data("/sub/data", "meta")
	assert not T.is_data("/sub")
	assert T.is_dir("/sub")
	assert not T.is_dir("/sub/data")
	assert T.is_data("/sub/data")

def test_deletion():
	meta1 = "apple"
	meta2 = "microsoft"
	meta3 = "linux"
	T = BlobTree(strdict())
	T.create_subtree("/sub", meta1)
	T.create_subtree("/sub/sub", meta2)
	T.create_data("/sub/data", meta3)
	T.set_data("/sub/data", "some data")
	assert "sub" in T.list_dir("/")
	T.unlink("/sub")
	assert not "sub" in T.list_dir("/")

def test_dir():
	meta1 = "apple"
	T = BlobTree(strdict())
	T.create_subtree("/sub", meta1)
	T.create_subtree("/sub/sub", meta1)
	T.create_subtree("/sub/sub2", meta1)

	assert "sub" in T.list_dir("")
	assert "sub" in T.list_dir("/")
	assert "sub" in T.list_dir("/sub")
	assert "sub2" in T.list_dir("/sub")

def test_rename():
	T = BlobTree(strdict())
	T.create_subtree("/sub", "meta")
	T.rename("/sub", "/dir")
	assert "dir" in T.list_dir("/")
	assert not "sub" in T.list_dir("/")
	# and again with changing directory
	T.create_data("/dir/sub", "meta")
	assert "sub" in T.list_dir("/dir")
	T.rename("/dir/sub", "/blub")
	assert "blub" in T.list_dir("/")
	assert not "sub" in T.list_dir("/dir")
	

if __name__ == "__main__":
	test_basic()
