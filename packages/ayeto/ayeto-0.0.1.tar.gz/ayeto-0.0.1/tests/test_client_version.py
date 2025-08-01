from ayeto import AyetoClient

def test_get_version():
    """Test to ensure the client can retrieve the version."""
    client = AyetoClient()
    version = client.get_version()
    assert version is not None