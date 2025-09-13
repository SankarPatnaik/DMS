import os, io, hashlib, boto3

def sha256_fileobj(fileobj: io.BytesIO) -> str:
    pos = fileobj.tell()
    fileobj.seek(0)
    d = hashlib.sha256()
    for chunk in iter(lambda: fileobj.read(8192), b""):
        d.update(chunk)
    fileobj.seek(pos)
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

    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream"):
        self.client.create_bucket(Bucket=self.bucket) if not self._bucket_exists() else None
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def _bucket_exists(self) -> bool:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False
