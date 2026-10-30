def test_login_fails_with_wrong_password(client):
    response = client.post('/login', data={'email': 'dev@test.com', 'password': 'wrongpass'})
    assert b'Invalid email or password' in response.data

def test_login_succeeds(client):
    response = client.post('/login', data={'email': 'dev@test.com', 'password': 'pass'}, follow_redirects=True)
    assert b'Dashboard' in response.data