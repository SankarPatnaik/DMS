"""Minimal stub of moto.mock_s3 used for tests.
This implementation provides an in-memory S3-like storage that patches
``boto3.client`` when used as a context manager.
"""
from __future__ import annotations

from contextlib import contextmanager
import boto3
import botocore.exceptions
import io
from typing import Dict


class _FakeS3Client:
    def __init__(self, storage: Dict[str, Dict[str, bytes]]) -> None:
        self._storage = storage

    # Bucket management -------------------------------------------------
    def create_bucket(self, Bucket: str) -> None:
        self._storage.setdefault(Bucket, {})

    def head_bucket(self, Bucket: str) -> None:
        if Bucket not in self._storage:
            error_response = {"Error": {"Code": "404"}}
            raise botocore.exceptions.ClientError(error_response, "HeadBucket")

    # Object operations -------------------------------------------------
    def put_object(self, Bucket: str, Key: str, Body: bytes, ContentType: str | None = None) -> None:
        self._storage.setdefault(Bucket, {})[Key] = Body

    def get_object(self, Bucket: str, Key: str):
        body = self._storage[Bucket][Key]
        return {"Body": io.BytesIO(body)}

    def list_objects_v2(self, Bucket: str):
        objects = self._storage.get(Bucket, {})
        return {"KeyCount": len(objects), "Contents": [{"Key": k} for k in objects]}


@contextmanager
def mock_s3():
    storage: Dict[str, Dict[str, bytes]] = {}
    original_client = boto3.client

    def client(service_name: str, *args, **kwargs):
        if service_name == "s3":
            return _FakeS3Client(storage)
        return original_client(service_name, *args, **kwargs)

    boto3.client = client
    try:
        yield
    finally:
        boto3.client = original_client
