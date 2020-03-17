

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
