from auth.oauth_callback_server import get_oauth_redirect_uri

def test_get_oauth_redirect_uri_prioritizes_env_var(monkeypatch):
    """
    Test that get_oauth_redirect_uri prioritizes the GOOGLE_OAUTH_REDIRECT_URI
    environment variable over the constructed URI.
    """
    # Set the environment variable
    expected_uri = "https://my-custom-redirect.uri/callback"
    monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", expected_uri)

    # Call the function with parameters that would otherwise construct a different URI
    redirect_uri = get_oauth_redirect_uri(
        port=8888,
        base_uri="http://should-be-ignored"
    )

    # Assert that the environment variable's value is returned
    assert redirect_uri == expected_uri

def test_get_oauth_redirect_uri_constructs_uri_when_env_var_is_missing(monkeypatch):
    """
    Test that get_oauth_redirect_uri constructs the URI from its parameters
    when the GOOGLE_OAUTH_REDIRECT_URI environment variable is not set.
    """
    # Ensure the environment variable is not set
    monkeypatch.delenv("GOOGLE_OAUTH_REDIRECT_URI", raising=False)

    # Call the function with specific parameters
    redirect_uri = get_oauth_redirect_uri(
        port=9999,
        base_uri="http://localhost-test"
    )

    # Assert that the URI is constructed as expected
    expected_uri = "http://localhost-test:9999/oauth2callback"
    assert redirect_uri == expected_uri