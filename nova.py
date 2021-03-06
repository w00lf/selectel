import os
import inspect
import argparse
from constants import *
from init_nova_client import *
import httplib
import json

parser = argparse.ArgumentParser(description='Creates servers for openstack cloud.')
parser.add_argument('server_names', metavar='NAME1 NAME2', type=str, nargs='+', help='Server names to create')
parser.add_argument('--vcpu', dest='vcpu', default=1, type=int, help='Virtual CPU-s for each server')
parser.add_argument('--ram', dest='ram', default=512, type=int, help='Ram volume for each server, Megabytes')
parser.add_argument('--disk', dest='disk', default=10, type=int, help='Disk space for each server, Gigabytes')
parser.add_argument('--ruby', dest='with_ruby', type=str, help='Use image with preinstalled ruby?')

args = parser.parse_args()

SERVERS = args.server_names
SERVERS_COUNT = len(SERVERS)
RAM = args.ram
VCPU = args.vcpu
DISK = args.disk


nova = InitNovaClient.call(auth_url=AUTH_URL,
                            username=USERNAME,
                            password=PASSWORD,
                            domain_name=DOMAIN_NAME,
                            project_domain_name=PROJECT_DOMAIN_NAME,
                            project_id=PROJECT_ID,
                            version=VERSION)

IMAGE_WITH_RUBY = '061b63e6-e203-4247-a628-1b2a1d632fa8'
IMAGE_UBUNTU_14_04_64 = 'dfbcee74-e4c5-4788-a156-4bbc6403ca17'
TARGET_IMAGE = IMAGE_UBUNTU_14_04_64 if args.with_ruby is None else IMAGE_WITH_RUBY

# TODO: change for options
INTERNAL_NETWORK_ID='3fd2b832-5849-46dc-a03f-070f852e43ee'

SELECTEL_HOST = "api.selectel.ru"
SELECTEL_API_TOKEN = os.environ['OS_SELECTEL_TOKEN']

def manage_qoutas(prject_id, ram, vcpu, disk):
  quotas = get_project_quotas(prject_id)
  free_qoutas = compute_free_quotas(quotas)
  ram =  None if free_qoutas['compute_ram'] >= vcpu else quotas['project']['quotas_usage']['compute_ram'] + (ram - free_qoutas['compute_ram'])
  vcpu = None if free_qoutas['compute_cores'] >= vcpu else quotas['project']['quotas_usage']['compute_cores'] + (vcpu - free_qoutas['compute_cores'])
  base_disk = None if free_qoutas['volume_gigabytes_basic'] >= vcpu else quotas['project']['quotas_usage']['volume_gigabytes_basic'] + (disk - free_qoutas['volume_gigabytes_basic'])
  return set_quotas(prject_id, ram, vcpu, base_disk)

def set_quotas(prject_id, ram=None, vcpu=None, base_disk=None):
  conn = httplib.HTTPSConnection(SELECTEL_HOST)
  quotas_hash = {}
  if int(vcpu or 0) != 0:
    quotas_hash['compute_cores'] = vcpu
  if int(ram or 0) != 0:
    quotas_hash['compute_ram'] = ram
  if int(base_disk or 0) != 0:
    quotas_hash['volume_gigabytes_basic'] = base_disk
  conn.request("PATCH", "/vpc/resell/v1/quotas/projects/{0}".format(prject_id), json.dumps({ 'quotas': quotas_hash }), { 'X-token': SELECTEL_API_TOKEN, 'Content-Type' : 'application/json' })
  response = conn.getresponse()
  return response.read()

def compute_free_quotas(project_quotas):
  project_attrs = project_quotas['project']
  result = {}
  for key in project_attrs['quotas_usage']:
    result[key] = project_attrs['quotas'][key] - project_attrs['quotas_usage'][key]
  return result

def get_project_quotas(project_id):
  conn = httplib.HTTPSConnection("api.selectel.ru")
  conn.request("GET", "/vpc/resell/v1/projects/{0}".format(project_id), None, { 'X-token': SELECTEL_API_TOKEN })
  response = conn.getresponse()
  return json.loads(response.read())

manage_qoutas(PROJECT_ID, RAM * SERVERS_COUNT, VCPU * SERVERS_COUNT, DISK * SERVERS_COUNT)

existing_flavors = nova.flavors.findall(ram=RAM,vcpus=VCPU, disk=0)
flavor = existing_flavors[0] if len(existing_flavors) >= 1 else nova.flavors.create(name=SERVERS[0],ram=RAM,vcpus=VCPU, disk=0)

for server_name in SERVERS:
  block_device_mapping_v2=[{"boot_index": 0, "destination_type": "volume", "source_type": "image", "uuid": TARGET_IMAGE, "device_name": "vda", 'volume_type': "basic", "volume_size": DISK, 'volume_name': "disk-for-{0}".format(server_name) }]
  # TODO: Add key_name as console arg
  server = nova.servers.create( name=server_name, image=None, block_device_mapping_v2=block_device_mapping_v2, min_count=1, max_count=1, config_drive=True, key_name='mik_key', flavor=flavor.id, nics=[{ 'net-id': INTERNAL_NETWORK_ID }])
