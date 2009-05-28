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

if __name__ == "__main__":
	test_basic()
