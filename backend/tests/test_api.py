BOOK = {"title": "The Phoenix Project", "author": "Gene Kim", "status": "reading", "rating": 5}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_book(client):
    r = client.post("/api/books", json=BOOK)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["title"] == BOOK["title"]
    assert body["status"] == "reading"


def test_list_books(client):
    client.post("/api/books", json=BOOK)
    client.post("/api/books", json={"title": "Site Reliability Engineering", "author": "Google"})
    r = client.get("/api/books")
    assert r.status_code == 200
    assert [b["title"] for b in r.json()] == ["The Phoenix Project", "Site Reliability Engineering"]


def test_get_book_and_404(client):
    created = client.post("/api/books", json=BOOK).json()
    assert client.get(f"/api/books/{created['id']}").status_code == 200
    assert client.get("/api/books/999").status_code == 404


def test_update_book(client):
    created = client.post("/api/books", json=BOOK).json()
    updated = {**BOOK, "status": "finished", "rating": 4}
    r = client.put(f"/api/books/{created['id']}", json=updated)
    assert r.status_code == 200
    assert r.json()["status"] == "finished"
    assert r.json()["rating"] == 4


def test_delete_book(client):
    created = client.post("/api/books", json=BOOK).json()
    assert client.delete(f"/api/books/{created['id']}").status_code == 204
    assert client.get(f"/api/books/{created['id']}").status_code == 404


def test_validation_rejects_bad_rating(client):
    r = client.post("/api/books", json={**BOOK, "rating": 9})
    assert r.status_code == 422


def test_metrics_endpoint_exposes_request_counter(client):
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
