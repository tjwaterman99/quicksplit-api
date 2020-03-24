import time

from cli import Client,  Config
from app.models import Event


# This just checks the track function doesn't break, but doesn't gaurantee the logged
# events will actually land. IE if we add a required field this won't catch
# that the CLI doesn't include it.
def test_logging_events(db, user):
    config = Config()
    client = Client(config)
    result = client.track(name='test-event')
    assert result is None
