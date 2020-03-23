from app.proxies import mailer


def test_mailer_can_send(client, user):
    resp = mailer._send(route="/mail/send", to=user.email, content="test content", subject="test subject")
    assert resp.status_code == 202

def test_mailer_can_send_async(client, user):
    job = mailer._send_async(route="/mail/send", to=user.email, content="test content", subject="test subject")
    print(dir(job))
