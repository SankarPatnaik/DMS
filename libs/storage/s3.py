import os, io, hashlib, boto3
from typing import Iterable, Union, BinaryIO

def sha256_fileobj(fileobj: Union[BinaryIO, Iterable[bytes]]) -> str:
    """Calculate SHA256 checksum of a file-like object or byte iterator.

    The input may be any object with a ``read`` method (e.g. a file object)
    or an iterable yielding ``bytes`` chunks.
    The file object's current position is preserved.
    """
    d = hashlib.sha256()

    if hasattr(fileobj, "read"):
        pos = fileobj.tell()
        if hasattr(fileobj, "seek"):
            fileobj.seek(0)
        for chunk in iter(lambda: fileobj.read(8192), b""):
            d.update(chunk)
        if hasattr(fileobj, "seek"):
            fileobj.seek(pos)
    else:
        for chunk in fileobj:
            d.update(chunk)

    return d.hexdigest()

class S3Client:
    def __init__(self):
        self.endpoint = os.getenv("S3_ENDPOINT","http://localhost:9000")
        self.bucket = os.getenv("S3_BUCKET","dmf-dev")
        self.key = os.getenv("S3_ACCESS_KEY","minio")
        self.secret = os.getenv("S3_SECRET_KEY","minio123")
        self.client = boto3.client("s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret
        )

    def put_bytes(
        self,
        key: str,
        data: Union[bytes, BinaryIO, Iterable[bytes]],
        content_type: str = "application/octet-stream",
    ):
        """Upload data to S3.

        ``data`` may be raw bytes, a file-like object, or an iterator yielding
        byte chunks.
        """

        self.client.create_bucket(Bucket=self.bucket) if not self._bucket_exists() else None

        body: Union[bytes, BinaryIO]
        if isinstance(data, (bytes, bytearray)):
            body = data
        elif hasattr(data, "read"):
            body = data  # type: ignore[assignment]
        else:
            body = _IteratorStream(iter(data))

        self.client.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType=content_type)

    def _bucket_exists(self) -> bool:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False


class _IteratorStream:
    """Wrap an iterator of bytes to provide a file-like ``read`` method."""

    def __init__(self, iterator: Iterable[bytes]):
        self._iter = iter(iterator)

    def read(self, *_args):
        try:
            return next(self._iter)
        except StopIteration:
            return b""
