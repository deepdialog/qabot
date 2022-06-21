
"""
curl -k https://user:password@localhost:9200/your_index_name_below?pretty
"""

import os
import json
from opensearchpy import OpenSearch


current_dir = os.path.realpath(os.path.dirname(__file__))
index_name = os.environ.get('INDEX', 'qabot')
config_index_name = os.environ.get('CONFIG_INDEX', 'qabot_config')

host = os.environ.get('host', 'localhost')
port = int(os.environ.get('port', 9200))
auth = (
    os.environ.get('user', 'admin'),
    os.environ.get('pass', 'admin')
)

client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
    # ca_certs = ca_certs_path
)

response = client.indices.create(index_name, body=json.load(open(os.path.join(current_dir, 'index_settings.json'))), ignore=400)
response = client.indices.create(config_index_name, body={}, ignore=400)
