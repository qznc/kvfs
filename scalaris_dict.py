import json
import urllib2

class scalaris_dict:
	def __init__(self, url):
		"""url should point to jsonrpc.yaws"""
		self._url = url
	def _request(self, method, *params):
		msg = json.dumps({
			'version': '1.1', 
			'method': method,
			'params': params,
			'id': 0})
		headers = {"Content-type": 'application/json'}
		request = urllib2.Request(self._url, msg, headers)
		fh = urllib2.urlopen(request)
		return json.loads(fh.read())
	def __setitem__(self, key, value):
		ret = self._request('write', key, value)
		assert ret['result'] == "ok"
	def __getitem__(self, key):
		return self._request('read', key)['result']
	def __delitem__(self, key):
		"""WARNING: keys may reappear in seldom cases!
		Read: http://groups.google.com/group/scalaris/browse_thread/thread/ff1d9237e218799?pli=1
		"""
		ret = self._request('delete', key)
		assert 'ok' in ret['result']
	def __contains__(self, key):
		result = self._request('read', key)['result']
		if 'failure' in result and result['failure'] == 'not_found':
			return False
		return True

if __name__ == "__main__":
	d = sdict('http://localhost:8000/jsonrpc.yaws')
	d['blub'] = "grins"
	del d['blub']
	print 'blubb' in d
	print 'blub' in d

