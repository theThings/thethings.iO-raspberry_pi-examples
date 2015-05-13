import requests


urlroot='https://api.thethings.io/v2/things/'
token='oGx7Id4U5-qsWFsHmjo30WrwXT3a5D7KbHWsYSPe1Rg'
header={'Accept': 'application/json', 'Content-Type': 'application/json'}
url=urlroot+token

def ttwrite(var, value):
	data='{"values":[{"key": "' + var + '","value": "' + value + '"}]}'
	r = requests.post(url, headers=header, data=data)

