import io
import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from libs.storage.s3 import S3Client, sha256_fileobj

DATABASE_URL = os.getenv("DATABASE_URL","postgresql+psycopg://dmf:dmf@localhost:5432/dmf")
engine = create_engine(DATABASE_URL, future=True)

app = FastAPI(title="DMF DMS")

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status":"ok"}
    except Exception as e:
        return JSONResponse({"status":"error","detail":str(e)}, status_code=500)

@app.post("/docs")
async def upload_doc(file: UploadFile = File(...), title: str = Form(None)):
    try:
        content = await file.read()
        fileobj = io.BytesIO(content)
        checksum = sha256_fileobj(fileobj)
        doc_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        version_no = 1
        storage_key = f"docs/{doc_id}/v{version_no}/{file.filename}"
        s3 = S3Client()
        s3.put_bytes(storage_key, content, content_type=file.content_type or "application/octet-stream")

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO documents (id, title, folder_id, storage_key, size_bytes, checksum, mime_type,
                    classification, tags, metadata, created_by, current_version_id)
                VALUES (:id, :title, NULL, :storage_key, :size, :checksum, :mime, 'internal', '{}', '{}', 'system', :ver_id)
            """), dict(id=doc_id, title=title or file.filename, storage_key=storage_key,
                         size=len(content), checksum=checksum, mime=file.content_type or "application/octet-stream", ver_id=version_id))

            conn.execute(text("""
                INSERT INTO document_versions (id, document_id, version_no, storage_key, checksum, created_by)
                VALUES (:id, :doc_id, :vno, :key, :checksum, 'system')
            """), dict(id=version_id, doc_id=doc_id, vno=version_no, key=storage_key, checksum=checksum))

        return {"id": doc_id, "title": title or file.filename, "version_no": version_no, "storage_key": storage_key}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
