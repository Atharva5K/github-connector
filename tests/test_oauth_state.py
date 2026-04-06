from app.services.oauth_state import OAuthStateStore


def test_state_is_single_use():
    store = OAuthStateStore(ttl_seconds=60)

    state = store.issue_state()

    assert store.validate_and_consume(state) is True
    assert store.validate_and_consume(state) is False
