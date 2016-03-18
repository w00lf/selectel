import os
import inspect
import time
from keystoneauth1.identity import v3
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

AUTH_URL="https://example.com/identity/v3"
VERSION="2"

PROJECT_DOMAIN_NAME='DOMAIN'
PROJECT_ID='ID'
PASSWORD = os.environ['SELECTEL_PASSWORD']

DOMAIN_NAME='NAME'
USERNAME='NAME'

auth = v3.Password( auth_url=AUTH_URL,
                    username=USERNAME,
                    password=PASSWORD,
                    user_domain_name=DOMAIN_NAME,
                    project_domain_name=PROJECT_DOMAIN_NAME,
                    project_id=PROJECT_ID)

sess = session.Session(auth=auth)
nova = client.Client(VERSION, session=sess, http_log_debug=True)

# i = 0
# for server in nova.servers.list():
#   if i > 1:
#     continue
#   flavor = nova.flavors.get(server.flavor['id']).__dict__
#   print(server.name, flavor['id'], flavor['ram'], flavor['vcpus'])
#   i += 1

# 8 gigabytes, 4 vcpu
FLAVOR = 'bb44263a-a4de-4165-9bf0-7e8f3071ba20'
# 512 megabytes, 1 vcpu
LIGHT_FLAVOR = '00180ad7-e0d5-4b5d-a7c0-9692e6d81935'
IMAGE_WITH_RUBY = '061b63e6-e203-4247-a628-1b2a1d632fa8'
INTERNAL_NETWORK_ID='3fd2b832-5849-46dc-a03f-070f852e43ee'

block_device_mapping_v2=[{"boot_index": "0",
                          "destination_type": "volume",
                          "source_type": "image",
                          "uuid": IMAGE_WITH_RUBY,
                          "device_name": "vda",
                          'volume_type': "basic",
                          "volume_size": "10",
                          'volume_name': 'disk-for-absolute-nova-test-01' }]

server = nova.servers.create( name='absolute-nova-test',
                              image='',
                              block_device_mapping_v2=block_device_mapping_v2,
                              min_count=1,
                              max_count=1,
                              config_drive=True,
                              flavor=LIGHT_FLAVOR,
                              nics=[{ 'net-id': INTERNAL_NETWORK_ID }])

# nova.volumes.create_server_volume(server_id=server.id,volume_id=volume.id)
