import os
from keystoneauth1.identity import v3
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

class InitNovaClient:
  @classmethod
  def call(self, auth_url, username, password, domain_name, project_domain_name, project_id, version):
    auth = v3.Password( auth_url=auth_url, username=username, password=password, user_domain_name=domain_name, project_domain_name=project_domain_name, project_id=project_id)
    sess = session.Session(auth=auth)
    return client.Client(version, session=sess, http_log_debug=True)
