import pytest
from httpx import Client
from scim2_models import Group
from scim2_models import User

from scim2_client.engines.httpx import SyncSCIMClient


@pytest.fixture
def sync_client(httpserver):
    client = Client(base_url=f"http://localhost:{httpserver.port}")
    scim_client = SyncSCIMClient(
        client,
        resource_models=[User, Group],
    )
    scim_client.register_naive_resource_types()
    return scim_client
