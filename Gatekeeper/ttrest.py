import requests


urlroot='https://api.thethings.io/v2/things/'
token='MyToken'
header={'Accept': 'application/json', 'Content-Type': 'application/json'}
url=urlroot+token

def ttwrite(var, value):
	data='{"values":[{"key": "' + var + '","value": "' + value + '"}]}'
	r = requests.post(url, headers=header, data=data)

