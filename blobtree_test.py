#!/usr/bin/env python
# -!- encoding: utf8 -!-

from blobtree import BlobTree

def test_basic():
	msg = "Hello Wörld! How are you?"
	meta_msg = "Söme meta data"
	T = BlobTree(dict())
	T.create_data("/blub", meta_msg)
	T.set_data("/blub", msg)
	T.create_data("/second", "more meta data")
	assert meta_msg == T.get_meta_data("/blub")
	assert msg == T.get_data("/blub")
	print T.create_subtree("/sub", meta_msg)
	T.create_data("/sub/blub", meta_msg)
	T.set_data("/sub/blub", "some data")
	assert meta_msg == T.get_meta_data("/sub/blub")
	print T

def test_meta_data():
	meta1 = "apple"
	meta2 = "microsoft"
	meta3 = "linux"
	T = BlobTree(dict())
	T.create_subtree("/sub", meta1)
	T.create_subtree("/sub/sub", meta2)
	T.create_data("/sub/data", meta3)
	T.set_data("/sub/data", "some data")

	assert meta1 == T.get_meta_data("/sub")
	assert meta2 == T.get_meta_data("/sub/sub")
	assert meta3 == T.get_meta_data("/sub/data")

def test_deletion():
	meta1 = "apple"
	meta2 = "microsoft"
	meta3 = "linux"
	T = BlobTree(dict())
	T.create_subtree("/sub", meta1)
	T.create_subtree("/sub/sub", meta2)
	T.create_data("/sub/data", meta3)
	T.set_data("/sub/data", "some data")
	T.unlink("/sub")

if __name__ == "__main__":
	test_basic()
