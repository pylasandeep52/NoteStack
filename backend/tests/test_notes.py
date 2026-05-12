def test_create_note_requires_auth(client):
    response = client.post("/notes", json={"title": "x", "content": "y"})
    assert response.status_code == 401


def test_create_note_returns_201(auth_client):
    response = auth_client.post(
        "/notes",
        json={"title": "First", "content": "Hello", "tag_names": ["work"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First"
    assert body["content"] == "Hello"
    assert [t["name"] for t in body["tags"]] == ["work"]
    assert body["id"] > 0


def test_list_notes_returns_own_only(auth_client, second_user_token):
    auth_client.post("/notes", json={"title": "Alice note", "content": ""})

    # Switch to Bob using his token
    auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
    response = auth_client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_search_notes_by_query(auth_client):
    auth_client.post("/notes", json={"title": "Buy groceries", "content": "milk"})
    auth_client.post("/notes", json={"title": "Read book", "content": "physics"})

    response = auth_client.get("/notes", params={"q": "milk"})
    titles = [n["title"] for n in response.json()]
    assert titles == ["Buy groceries"]


def test_filter_notes_by_tag(auth_client):
    auth_client.post("/notes", json={"title": "A", "content": "", "tag_names": ["work"]})
    auth_client.post("/notes", json={"title": "B", "content": "", "tag_names": ["personal"]})
    auth_client.post("/notes", json={"title": "C", "content": "", "tag_names": ["work"]})

    response = auth_client.get("/notes", params={"tag": "work"})
    titles = sorted(n["title"] for n in response.json())
    assert titles == ["A", "C"]


def test_get_other_users_note_returns_404(auth_client, second_user_token):
    created = auth_client.post("/notes", json={"title": "Secret", "content": ""}).json()

    auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
    response = auth_client.get(f"/notes/{created['id']}")
    assert response.status_code == 404


def test_patch_updates_only_sent_fields(auth_client):
    created = auth_client.post(
        "/notes",
        json={"title": "Original", "content": "Body", "tag_names": ["a"]},
    ).json()

    response = auth_client.patch(
        f"/notes/{created['id']}",
        json={"title": "Updated"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated"
    assert body["content"] == "Body"
    assert [t["name"] for t in body["tags"]] == ["a"]


def test_patch_tag_names_replaces_tags(auth_client):
    created = auth_client.post(
        "/notes",
        json={"title": "T", "content": "", "tag_names": ["one", "two"]},
    ).json()

    response = auth_client.patch(
        f"/notes/{created['id']}",
        json={"tag_names": ["three"]},
    )
    assert response.status_code == 200
    assert [t["name"] for t in response.json()["tags"]] == ["three"]


def test_delete_note(auth_client):
    created = auth_client.post("/notes", json={"title": "Bye", "content": ""}).json()

    response = auth_client.delete(f"/notes/{created['id']}")
    assert response.status_code == 204

    get_response = auth_client.get(f"/notes/{created['id']}")
    assert get_response.status_code == 404


def test_delete_other_users_note_returns_404(auth_client, second_user_token):
    created = auth_client.post("/notes", json={"title": "Mine", "content": ""}).json()

    auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
    response = auth_client.delete(f"/notes/{created['id']}")
    assert response.status_code == 404


def test_pagination_limit(auth_client):
    for i in range(5):
        auth_client.post("/notes", json={"title": f"Note {i}", "content": ""})

    response = auth_client.get("/notes", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2
