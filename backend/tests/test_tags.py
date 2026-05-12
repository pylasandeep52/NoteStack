def test_list_tags_requires_auth(client):
    response = client.get("/tags")
    assert response.status_code == 401


def test_list_tags_returns_own_only(auth_client, second_user_token):
    auth_client.post(
        "/notes",
        json={"title": "Alice note", "content": "", "tag_names": ["alice-tag"]},
    )

    auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
    response = auth_client.get("/tags")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tags_alphabetical(auth_client):
    auth_client.post(
        "/notes",
        json={"title": "n", "content": "", "tag_names": ["zeta", "alpha", "mu"]},
    )

    response = auth_client.get("/tags")
    names = [t["name"] for t in response.json()]
    assert names == ["alpha", "mu", "zeta"]
