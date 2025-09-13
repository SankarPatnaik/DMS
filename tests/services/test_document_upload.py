import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

@pytest.fixture
def app_with_db(monkeypatch):
    """Provide app and in-memory database."""
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                folder_id TEXT,
                storage_key TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                classification TEXT NOT NULL,
                tags TEXT,
                metadata TEXT,
                created_by TEXT NOT NULL,
                current_version_id TEXT
            )
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE document_versions (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                version_no INTEGER NOT NULL,
                storage_key TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_by TEXT NOT NULL,
                UNIQUE(document_id, version_no)
            )
            """
        ))
    from apps.dms import main as dms_main
    monkeypatch.setattr(dms_main, "engine", engine)
    return dms_main.app, engine

@pytest.fixture
def s3_mock(monkeypatch):
    moto = pytest.importorskip("moto")
    from moto import mock_s3
    monkeypatch.setenv("S3_BUCKET", "test-bucket")
    monkeypatch.setenv("S3_ACCESS_KEY", "testing")
    monkeypatch.setenv("S3_SECRET_KEY", "testing")
    monkeypatch.setenv("S3_ENDPOINT", "https://s3.amazonaws.com")
    with mock_s3():
        yield

def test_upload_document_persists(app_with_db, s3_mock):
    app, engine = app_with_db
    client = TestClient(app)
    files = {"file": ("hello.txt", b"hello", "text/plain")}
    resp = client.post("/docs", data={"title": "hello"}, files=files)
    assert resp.status_code == 200
    doc_id = resp.json()["id"]
    with engine.connect() as conn:
        row = conn.execute(text("SELECT title FROM documents WHERE id=:id"), {"id": doc_id}).first()
        assert row is not None
    import boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    )
    obj = s3.get_object(Bucket=os.getenv("S3_BUCKET"), Key=resp.json()["storage_key"])
    assert obj["Body"].read() == b"hello"

def test_upload_document_s3_failure(app_with_db, monkeypatch):
    app, engine = app_with_db
    client = TestClient(app)
    def boom(self, key, data, content_type="application/octet-stream"):
        raise Exception("s3 boom")
    monkeypatch.setattr("libs.storage.s3.S3Client.put_bytes", boom)
    files = {"file": ("hello.txt", b"hello", "text/plain")}
    resp = client.post("/docs", data={"title": "hello"}, files=files)
    assert resp.status_code == 400
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM documents")).scalar_one()
        assert count == 0

def test_upload_document_db_failure(app_with_db, s3_mock, monkeypatch):
    app, engine = app_with_db
    import apps.dms.main as dms_main
    class BoomCtx:
        def __enter__(self):
            raise Exception("db boom")
        def __exit__(self, exc_type, exc, tb):
            pass
    monkeypatch.setattr(dms_main.engine, "begin", lambda *a, **k: BoomCtx())
    client = TestClient(app)
    files = {"file": ("hello.txt", b"hello", "text/plain")}
    resp = client.post("/docs", data={"title": "hello"}, files=files)
    assert resp.status_code == 400
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM documents")).scalar_one()
        assert count == 0
    import boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    )
    resp = s3.list_objects_v2(Bucket=os.getenv("S3_BUCKET"))
    assert resp.get("KeyCount", 0) == 1
