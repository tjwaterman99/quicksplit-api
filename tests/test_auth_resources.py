

def test_logged_in_session(user, password, email, db, logged_out_client):
    client = logged_out_client
    with client.session_transaction() as sess:
        resp = client.post('/sessions', json={
            'email': email,
            'password': password
        })
        assert 'Set-Cookie' in resp.headers

        resp2 = client.get('/user')
        assert resp.status_code == 200
        assert resp2.json['data']['id'] == str(user.id)
        assert len(user.sessions.all()) == 1

        resp3 = client.delete('/sessions')
        assert resp3.status_code == 200
        assert len(user.sessions.all()) == 0

        resp4 = client.get('/user')
        assert resp4.status_code == 403


def test_loading_session(user, password, email, db, logged_out_client, exposure):
    client = logged_out_client
    with client.session_transaction() as sess:
        resp = client.post('/sessions', json={
            'email': email,
            'password': password
        })

        resp2 = client.get('/recent')
        assert resp2.status_code == 200
        assert len(resp2.json['data']) == 1

        resp3 = client.get('/recent', json={'environment': 'staging'})
        assert  resp3.status_code == 200
        assert len(resp3.json['data']) == 0

        resp4 = client.get('/recent', json={'environment':  'production'})
        assert resp4.status_code == 200
        assert len(resp4.json['data']) == 1

        resp5 = client.post('/exposures', json={
            'subject': 1234,
            'experiment': exposure.experiment.name,
            'cohort': 'experimental',
            'environment': 'staging'
        })
        assert resp5.status_code == 200
        assert resp5.json['data']['scope']['name'] == 'staging'

        resp6 = client.get('/recent', json={'environment': 'staging'})
        assert resp6.status_code == 200
        assert len(resp6.json['data'])  == 1
