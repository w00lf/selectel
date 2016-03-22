import os
import csv
import inspect
import argparse
from constants import *
from init_nova_client import *
from datetime import date

parser = argparse.ArgumentParser(description='Creates report for servers.')
parser.add_argument('--server_names', dest='server_names', metavar='NAME1 NAME2', default=[], type=str, nargs='+', help='Server names to create report for')
args = parser.parse_args()

# Prices for one item, rub
MEMORY_WEIGHT = 0.1401151631477927
DISK_WEIGHT = 7.3
FAST_DISK_WEIGHT = 44
CPU_WEIGHT = 402

nova_client = InitNovaClient.call(auth_url=AUTH_URL,
                                      username=USERNAME,
                                      password=PASSWORD,
                                      domain_name=DOMAIN_NAME,
                                      project_domain_name=PROJECT_DOMAIN_NAME,
                                      project_id=PROJECT_ID,
                                      version=VERSION)

cached_volumes = nova_client.volumes.list()
RESULT_FILE = "selectel-{0}.csv".format(date.today())
SERVER_NAMES_PROVIDED = len(args.server_names) > 0

with open(RESULT_FILE, 'wb') as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(['Id', 'Name', 'Memory', 'Disks(fast)', 'Disks(base)', 'CPU cores', 'Total cost'])
  for server in nova_client.servers.list():

    if SERVER_NAMES_PROVIDED and server.name not in args.server_names:
      continue

    flavor = nova_client.flavors.get(server.flavor['id'])

    disks_base = 0
    disks_fast = 0

    for volume in cached_volumes:
      attachments = volume.attachments
      if len(attachments) == 0 or attachments[0]['server_id'] != server.id:
        continue
      if volume.volume_type == 'basic':
        disks_base += volume.size
      if volume.volume_type == 'fast':
        disks_fast += volume.size

    total_cost = (flavor.ram * MEMORY_WEIGHT) + (flavor.vcpus * CPU_WEIGHT) + (disks_base * DISK_WEIGHT) + (disks_fast * FAST_DISK_WEIGHT);

    writer.writerow([server.id, server.name, flavor.ram, disks_fast, disks_base, flavor.vcpus, total_cost])


print("Finished, report file: {0}".format(RESULT_FILE))
