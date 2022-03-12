import requests
import xml.etree.ElementTree as ET
import sys

def make_request(url):
	resp = requests.get(url)
	if resp.status_code == 200:
		return resp.content

def scraping(host_and_port, info):
	try:
		content = make_request(f"http://{host_and_port}/admin?op=stats")
		tree = ET.fromstring(content)

		server_stats = tree.find(".//{http://xmlns.endeca.com/ene/dgraph}server_stats/{http://xmlns.endeca.com/ene/dgraph}stat[@name='HTTP: Total request time']")

		if info == 'requests':
			return server_stats.attrib.get('n')

		if info == 'response_time_avg':
			return server_stats.attrib.get('avg')
		
		return "argumentos errados ex.: py dgraph.py livemdex:13030 <requests || response_time_avg>"
		
	except Exception as e:
		print('error: scraping', e)
		return 0

if __name__ == '__main__':
	if(len(sys.argv) != 3):
		print("Falta argumentos, ex.: py dgraph.py livemdex:13030 <requests || response_time_avg>")
	else:
		print(scraping(sys.argv[1], sys.argv[2]))
	