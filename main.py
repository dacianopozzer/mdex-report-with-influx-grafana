import requests
import xml.etree.ElementTree as ET
from sshtunnel import open_tunnel
import tempfile
import time

from influxdb import InfluxDBClient

# Disable SSL warning 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)

WITH_TUNNEL = True
SSH_TUNEL_HOST = 'ocauxiliary2'
SSH_USER = '******'
SSH_PWD = '******'

client = InfluxDBClient(host="localhost", port='8086', 
        username='ecommerce', password='******', database='dgraphs_statistics',
        ssl=True, cert=("ssl/influxdb-selfsigned.crt","ssl/influxdb-selfsigned.key"))


class Server:
    def __init__(self, host, instanceName, port):
        self.host = host
        self.port = port
        self.instanceName = instanceName

servers=[
    Server('****:12030','livemdex1','12030'),
    Server('****:12030','livemdex2','12030'),
    
    #Server('****:13020','***livemdex3','13020'),
    #Server('****:13020','***livemdex4','13020')	
]

def make_request(url):
	resp = requests.get(url)
	if resp.status_code == 200:
		return resp.content
	
	return ""


def get_content(host_and_port):
	if WITH_TUNNEL:
		host, port = host_and_port.split(':')
		with open_tunnel(
			SSH_TUNEL_HOST,
			ssh_username=SSH_USER,
			ssh_password=SSH_PWD,
			remote_bind_address=(host, int(port))
		) as server:
			return make_request(f"http://127.0.0.1:{server.local_bind_port}/admin?op=stats")
	else:
		return make_request(f"http://{host_and_port}/admin?op=stats")



def scraping(host_and_port):
	try:
		measurement = {}
		content = get_content(host_and_port)
		tree = ET.fromstring(content)

		measurement['measurement'] = 'dgraphs_report'
		measurement['tags'] = {}
		measurement['fields'] = {}

		general_information = tree.find('{http://xmlns.endeca.com/ene/dgraph}general_information')
		dgraph_process_information = general_information.find('{http://xmlns.endeca.com/ene/dgraph}dgraph_process_information')
		measurement['tags']['host'] = dgraph_process_information.attrib.get('hostname')
		measurement['tags']['port'] = dgraph_process_information.attrib.get('server_port')

		throughput = tree.find('{http://xmlns.endeca.com/ene/dgraph}performance_summary/{http://xmlns.endeca.com/ene/dgraph}throughput')
		measurement['fields']['throughput_one_min'] = float(throughput.attrib.get('one_minute_avg'))
		measurement['fields']['throughput_five_min'] = float(throughput.attrib.get('five_minute_avg'))
		measurement['fields']['throughput_ten_min'] = float(throughput.attrib.get('ten_second_avg'))


		cache_stats = tree.find(".//{http://xmlns.endeca.com/ene/dgraph}main_cache/{http://xmlns.endeca.com/ene/dgraph}cache_stats[@name='Totals']")
		measurement['fields']['entry_count'] = int(cache_stats.attrib.get('entry_count').replace('nan','0'))
		measurement['fields']['all_entries_size_mb'] = float(cache_stats.attrib.get('all_entries_size_mb').replace('nan','0'))
		measurement['fields']['num_lookups'] = float(cache_stats.attrib.get('num_lookups').replace('nan','0'))
		measurement['fields']['hit_pct'] = float(cache_stats.attrib.get('hit_pct').replace('nan','0'))
		measurement['fields']["miss_pct"] = float(cache_stats.attrib.get("miss_pct").replace('nan','0'))

		server_stats = tree.find(".//{http://xmlns.endeca.com/ene/dgraph}server_stats/{http://xmlns.endeca.com/ene/dgraph}stat[@name='HTTP: Total request time']")
		measurement['fields']['stat_requests'] = int(server_stats.attrib.get('n').replace('nan','0'))
		measurement['fields']['stat_requests_max'] = float(server_stats.attrib.get('max').replace('nan','0'))		
		measurement['fields']['stat_requests_avg'] = float(server_stats.attrib.get('avg').replace('nan','0'))

		stat_page = tree.find(".//{http://xmlns.endeca.com/ene/dgraph}result_page_stats/{http://xmlns.endeca.com/ene/dgraph}stat[@name='Result page format performance']")
		measurement['fields']['stat_page_avg'] = float(stat_page.attrib.get('avg').replace('nan','0'))
		measurement['fields']['stat_page_min'] = float(stat_page.attrib.get('min').replace('nan','0'))
		measurement['fields']['stat_page_max'] = float(stat_page.attrib.get('max').replace('nan','0'))

		stat_nav_avg = tree.find(".//{http://xmlns.endeca.com/ene/dgraph}navigation/{http://xmlns.endeca.com/ene/dgraph}stat[@name='Navigation Performance']")
		measurement['fields']['stat_nav_avg'] = float(stat_nav_avg.attrib.get('avg').replace('nan','0'))
		measurement['fields']['stat_nav_min'] = float(stat_nav_avg.attrib.get('min').replace('nan','0'))
		measurement['fields']['stat_nav_max'] = float(stat_nav_avg.attrib.get('max').replace('nan','0'))		

		return measurement
	except Exception as e:
		print('error: scraping', e)
		return ""

def send_influx(measurement) :

	try:
		client.write_points(measurement, database='dgraphs_statistics', time_precision=None, batch_size=10000, protocol='json')
	except Exception as e:
		print('deu ruim', e)


if __name__ == '__main__':

	while True: 
		
		measurements = []

		for server in servers:
			print(server.host, server.instanceName )
			measurement = scraping(server.host)
			measurements.append(measurement)
			time.sleep(0.2)
	
		send_influx(measurements)
		#print('------------------------------------------------ send OK \n',measurements)
		print("----------------- SEND OK")
		time.sleep(300)


	