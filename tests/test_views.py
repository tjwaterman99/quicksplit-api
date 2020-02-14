
def test_root_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
