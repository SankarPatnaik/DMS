-- Alembic raw SQL migration
-- revision id: 0001_init
-- down revision: none

CREATE TABLE IF NOT EXISTS folders (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  parent_id UUID,
  owner_org_unit TEXT,
  path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  folder_id UUID REFERENCES folders(id),
  storage_key TEXT NOT NULL,
  size_bytes BIGINT NOT NULL,
  checksum TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  classification TEXT NOT NULL DEFAULT 'internal',
  tags TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_by TEXT NOT NULL DEFAULT 'system',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  current_version_id UUID
);

CREATE TABLE IF NOT EXISTS document_versions (
  id UUID PRIMARY KEY,
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version_no INT NOT NULL,
  storage_key TEXT NOT NULL,
  checksum TEXT NOT NULL,
  created_by TEXT NOT NULL DEFAULT 'system',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  change_note TEXT,
  UNIQUE(document_id, version_no)
);

CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin ON documents USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_documents_tags_gin     ON documents USING GIN (tags);
