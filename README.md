# TactivAI Knowledge Base Upload Tool

A desktop application for uploading markdown knowledge base articles to Supabase with OpenAI vector embeddings. Designed for RAG (Retrieval Augmented Generation) applications.

## Features

- **Simple GUI** - No command line required
- **Vector Embeddings** - Automatically generates embeddings using OpenAI's `text-embedding-3-small` model
- **Duplicate Detection** - Skips files already uploaded to prevent duplicates
- **Progress Tracking** - Real-time progress bar and detailed logging
- **Connection Validation** - Test your API credentials before uploading

## Download

Download the latest release from the [Releases](../../releases) page:
- `TactivAI-KB-Upload.exe` - Standalone Windows executable (no Python required)

## Requirements (for running from source)

- Python 3.10+
- OpenAI API key
- Supabase project with pgvector enabled

### Python Dependencies

```bash
pip install openai httpx
```

## Supabase Setup

Your Supabase project needs:

1. **pgvector extension enabled**
2. **A `documents` table** with this schema:

```sql
-- Enable pgvector extension
create extension if not exists vector;

-- Create documents table
create table documents (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(1536)
);

-- Create similarity search function
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 5
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;
```

## Article Format

Articles should be markdown files (`.md`) with YAML frontmatter:

```markdown
---
id: HT-001
title: How to Reset Your Windows Password
category: How-To Guide
audience: End-User
domain: Windows
tags: password, reset, windows, login
priority: P1-CRITICAL
---

# How to Reset Your Windows Password

## When to Use This Article
Use this guide when you've forgotten your Windows password...

## Step-by-Step Instructions

### Step 1: Access the Login Screen
...
```

## Usage

1. **Launch the app** - Run `TactivAI-KB-Upload.exe` or `python upload_app.py`
2. **Select folder** - Browse to your folder containing `.md` files
3. **Enter credentials**:
   - OpenAI API Key
   - Supabase URL (e.g., `https://your-project.supabase.co`)
   - Supabase Service Role Key (found in Settings > API)
4. **Click Upload** - The tool validates connections, checks for duplicates, and uploads

## Article Generator

The `generate_articles.py` script uses OpenAI GPT-4o-mini to generate knowledge base articles:

```bash
python generate_articles.py
```

This creates articles in category subfolders:
- `generated-articles/how-to-guides/`
- `generated-articles/troubleshooting/`
- `generated-articles/solutions/`
- `generated-articles/runbooks/`

## Knowledge Base Structure

- **How-To Guides (HT):** Step-by-step instructions for common tasks
- **Troubleshooting Guides (TS):** Diagnostic flows for issues
- **Solution Articles (SOL):** Specific fixes for known problems
- **Runbooks (RB):** IT admin procedures

## Project Structure

```
TactivAI-KB/
├── upload_app.py          # Main upload tool (Tkinter GUI)
├── generate_articles.py   # AI article generator
├── demo-articles/         # Sample articles
├── dist/                  # Built executables
└── README.md
```

## Building the Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TactivAI-KB-Upload" upload_app.py
```

The executable will be in the `dist/` folder.

## License

MIT License

## Support

For issues or questions, please open a GitHub issue.
