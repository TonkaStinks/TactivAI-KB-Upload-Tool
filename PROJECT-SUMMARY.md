# TactivAI Tech Support Voice Assistant - Complete Project Summary

**Last Updated:** February 6, 2026
**GitHub:** https://github.com/TonkaStinks/TactivAI-KB-Upload-Tool

---

## What This Project Is

A voice-based IT tech support assistant that answers questions by searching a knowledge base of 155 articles using RAG (Retrieval Augmented Generation). Callers dial a phone number, describe their issue, and the assistant diagnoses the problem through targeted questions, then walks them through a solution step-by-step. If the KB can't answer, the call is transferred to a human. After resolution, the assistant can email a summary.

---

## Architecture

```
User (Voice Call to +15087940446)
    |
VAPI (Voice AI - Speech-to-Text + LLM + Text-to-Speech)
    |
    |-- Tool: TactivAI_Demo_KB --> n8n Webhook --> OpenAI Embeddings --> Supabase pgvector --> Response
    |-- Tool: TactivAI_transfer_call --> Blind transfer to +15082827112
    |-- Tool: TactivAI_send_summary --> n8n Webhook --> Gmail (pending setup)
```

---

## All Services & Credentials Needed

| Service | Purpose | URL/Info |
|---------|---------|----------|
| **VAPI** | Voice AI platform | vapi.ai - hosts assistant, phone number, tools |
| **n8n** | Workflow automation | opendealflow.app.n8n.cloud - webhooks for KB search and email |
| **Supabase** | Vector database | udgqspastvroptzxfuug.supabase.co - pgvector similarity search |
| **OpenAI** | Embeddings | text-embedding-3-small (1536 dimensions) |
| **GitHub** | Code repo | github.com/TonkaStinks/TactivAI-KB-Upload-Tool |

### Credentials Required
- OpenAI API Key
- Supabase URL: `https://udgqspastvroptzxfuug.supabase.co`
- Supabase Service Role Key (not anon key)
- VAPI account with phone number

---

## VAPI Configuration

### Assistant: `TactivAI_Demo_KB`
- **Phone Number:** `+15087940446` (Inbound)
- **Assistant Name:** Evan (bilingual English/Spanish)
- **Inbound Settings:** Assistant set to `TactivAI_Demo_KB`

### VAPI Tools (3 total, all attached to assistant)

#### 1. TactivAI_Demo_KB (Knowledge Base Search)
- **Type:** Custom Tool (webhook)
- **Server URL:** `https://opendealflow.app.n8n.cloud/webhook/9ddfb8d7-d88f-4d62-8127-ff5e9bdb92f2`
- **Parameter:** `question` (string)
- **Purpose:** Searches KB via n8n -> Supabase vector search

#### 2. TactivAI_transfer_call (Escalation)
- **Type:** Transfer Call
- **Destination:** `+15082827112` (E.164 format required)
- **Transfer Mode:** Blind Transfer
- **Message:** "Let me connect you with one of our support specialists. Please hold for just a moment."
- **Note:** Only works on real phone calls, NOT on web "Talk to Assistant"

#### 3. TactivAI_send_summary (Email Summary)
- **Type:** Custom Tool (webhook)
- **Server URL:** `https://opendealflow.app.n8n.cloud/webhook/63dde889-fc92-46ce-950b-1bf7b9e81605`
- **Parameters:** email, caller_name, issue_summary, resolution_summary, status
- **Status:** Tool configured. n8n webhook created. Gmail node NOT yet connected (waiting for support@tactivai.com password from Dave).

---

## VAPI System Prompt (Current Version)

The prompt has these major sections:

1. **CRITICAL CONVERSATION RULES** - Always ask for name first, make forward progress every turn, no idle phrases
2. **IDENTITY & LANGUAGE** - Evan, bilingual English/Spanish, auto-detect language
3. **NAME HANDLING** - Confirm name, strict rules on corrections, use name only at closing
4. **KNOWLEDGE BASE USAGE** - Specific questions search KB immediately; vague issues go through diagnostic first
5. **ISSUE INTAKE - DIAGNOSE BEFORE YOU SOLVE** - 5-step flow:
   - Acknowledge the issue
   - Determine if triage is needed (vague vs specific)
   - Ask 2-3 diagnostic questions (ONE at a time)
   - Summarize what you learned, THEN search KB with targeted query
   - Deliver solution step-by-step
6. **DIAGNOSTIC QUESTION GUIDES** - Topic-specific questions for: Printer, Email/Outlook, Network/WiFi, Teams, Computer Performance, Login/Account, MFA, OneDrive, General Fallback
7. **STEP-BY-STEP DELIVERY** - Walk through ONE step at a time, varied check-in phrases, never dump all steps at once
8. **GLOBAL ANSWER HANDLING** - Treat short answers as valid, acknowledge and continue
9. **SILENCE/MISHEARING HANDLING** - Repeat after 5s silence, ask to speak up if consistent
10. **TROUBLESHOOTING SUCCESS** - Confirm fix with "everything working normally now?"
11. **EMAIL SUMMARY** - After success, offer email summary, spell out email, use TactivAI_send_summary tool
12. **ESCALATION & CALL TRANSFER** - 6 trigger conditions, use TactivAI_transfer_call tool
13. **CLOSING** - "Thanks for calling - have a great day." (once, then stop)

---

## n8n Workflows

### Workflow 1: KB Search
- **Production URL:** `https://opendealflow.app.n8n.cloud/webhook/9ddfb8d7-d88f-4d62-8127-ff5e9bdb92f2`
- **Test URL:** `https://opendealflow.app.n8n.cloud/webhook-test/9ddfb8d7-d88f-4d62-8127-ff5e9bdb92f2`
- **Nodes:** Webhook -> Supabase Vector Store -> Clean Content -> Respond to Webhook
- **Question path in n8n:** `{{ $json.body.message.toolCalls[0].function.arguments.question }}`
- **CRITICAL:** After changes, must click **Publish** (not just Save)

### Workflow 2: Email Summary (Incomplete)
- **Production URL:** `https://opendealflow.app.n8n.cloud/webhook/63dde889-fc92-46ce-950b-1bf7b9e81605`
- **Status:** Webhook created. Gmail node needs password for support@tactivai.com
- **TODO:** Add Gmail node, format email template, test end-to-end

---

## Supabase Database

### Table: `documents`
| Column | Type | Description |
|--------|------|-------------|
| id | int8 | Auto-incrementing primary key |
| content | text | Full markdown article content |
| metadata | jsonb | `{"category": "...", "filename": "..."}` |
| embedding | vector(1536) | OpenAI text-embedding-3-small vector |

### Function: `match_documents`
```sql
create or replace function match_documents (
  query_embedding vector(1536),
  match_count int default 5,
  filter jsonb default '{}'
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select id, content, metadata,
    1 - (embedding <=> query_embedding) as similarity
  from documents
  order by embedding <=> query_embedding
  limit match_count;
$$;
```

### Current Data (155 articles)
- IDs 155-163: Original 9 demo articles (hand-written)
- IDs 164+: 146 AI-generated articles (GPT-4o-mini)

**Categories uploaded with these tags:**
- `demo-articles` (9 articles)
- `how-to-guides` (46 articles)
- `troubleshooting` (30 articles)
- `solutions` (45 articles)
- `runbooks` (25 articles)

---

## Knowledge Base Content

### Original 9 Demo Articles (IDs 155-163)
| ID | Filename | Topic |
|----|----------|-------|
| 155 | HT-001-How-to-Reset-Windows-Password.md | Windows password reset |
| 156 | HT-002-How-to-Connect-iPhone-to-Company-Email.md | iOS email setup |
| 157 | HT-003-How-to-Set-Up-VPN.md | VPN connection |
| 158 | HT-007-How-to-Connect-to-Office-WiFi.md | WiFi connection |
| 159 | HT-008-How-to-Print-to-Network-Printer.md | Network printer |
| 160 | FAQ-001-Is-Dave-Hynes-Technical.md | Fun article (Dave is NOT technical!) |
| 161 | HT-004-How-to-Clear-Browser-Cache.md | Browser cache |
| 162 | HT-005-How-to-Join-Teams-Meeting.md | Teams meetings |
| 163 | TS-001-Troubleshoot-Slow-Computer.md | Slow computer |

### 146 AI-Generated Articles (by category)
- **How-To Guides (HT-003 to HT-050):** 46 articles - MFA setup, OneDrive, screen sharing, out of office, calendar, email forwarding, printers, bluetooth, display, etc.
- **Troubleshooting (TS-001 to TS-030):** 30 articles - Network, email sync, Teams audio/video, account lockout, printer, WiFi, keyboard, mouse, webcam, USB, etc.
- **Solutions (SOL-001 to SOL-045):** 45 articles - DNS fixes, cache clearing, profile rebuilds, network resets, print spooler, credential manager, etc.
- **Runbooks (RB-001 to RB-025):** 25 articles - User provisioning, password resets, MFA resets, license management, mailbox access, compliance, retention, etc.

---

## Files & Tools

### Key Files
| File | Purpose |
|------|---------|
| `upload_app.py` | **Main tool** - Tkinter GUI for uploading articles to Supabase |
| `generate_articles.py` | AI article generator using GPT-4o-mini |
| `demo-articles/` | 9 hand-written demo articles |
| `generated-articles/` | 146 AI-generated articles in 4 subfolders |
| `PROJECT-SUMMARY.md` | This file |
| `README.md` | GitHub repo README |
| `.gitignore` | Git ignore rules |

### Executable
- `dist/TactivAI-KB-Upload.exe` - Standalone Windows executable (67 MB)
- Built with PyInstaller: `pyinstaller --onefile --windowed --name "TactivAI-KB-Upload" upload_app.py`
- Upload as GitHub Release (too large for git)

### Legacy/Reference Files (not in GitHub)
| File | Purpose |
|------|---------|
| `upload_demo.py` | Original upload script (hardcoded keys) |
| `upload_new_articles.py` | Upload script for 4 new articles |
| `upload_kb.py` | CLI upload tool (superseded by upload_app.py) |
| `test_search.py` / `test_search2.py` | Search testing scripts |
| `01-How-To-Guides/` etc. | Original placeholder article folders (content was templates) |

---

## VAPI Request/Response Format

### What n8n receives from VAPI:
```json
{
  "body": {
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_XU5OZcYiEfmo1DypUALHGVk6",
        "type": "function",
        "function": {
          "name": "TactivAI_Demo_KB",
          "arguments": {
            "question": "user's question here"
          }
        }
      }]
    }
  }
}
```

### Upload format for Supabase:
```json
{
  "content": "Full markdown content as string",
  "metadata": {"category": "how-to-guides", "filename": "HT-003-How-to-Set-Up-MFA.md"},
  "embedding": [0.123, -0.456, ...]
}
```

---

## Article Format (Markdown)

```markdown
---
id: HT-001
title: How to Reset Your Windows Password
category: How-To Guide
audience: End-User
domain: Windows
tags: password, login, security, reset, locked out
priority: P1-CRITICAL
related_articles: []
last_updated: 2024-12-11
---

# How to Reset Your Windows Password

## When to Use This Article
[1-2 sentences]

## Prerequisites
- [List 2-4]

## Step-by-Step Instructions

### Step 1: [Action]
[Detailed instructions]

### Step 2: [Action]
[Detailed instructions]

## Common Issues

### Issue 1: [Problem]
**Symptoms:** [What user sees]
**Solution:** [Fix]

## Escalation Triggers
- [When to escalate]

## Success Criteria
- [How to verify]
```

---

## Known Issues & Troubleshooting

| # | Issue | Cause | Fix |
|---|-------|-------|-----|
| 1 | Low similarity scores (0.1-0.2) | Embedding model mismatch | Both upload AND search must use `text-embedding-3-small` |
| 2 | n8n returns empty response | Workflow not published | Must click **Publish**, not just Save |
| 3 | "Cannot embed empty text" error | Wrong path in n8n | Use `{{ $json.body.message.toolCalls[0].function.arguments.question }}` |
| 4 | Returns wrong/irrelevant articles | Placeholder articles in DB | Delete placeholders, keep only real content |
| 5 | 404 errors in VAPI logs | VAPI sends multiple webhook types | Normal - can ignore |
| 6 | Transfer fails on web "Talk to Assistant" | Web doesn't support transfers | Must test on real phone calls |
| 7 | Transfer loops (says it will transfer but doesn't) | Tool not added to assistant | Add TactivAI_transfer_call to assistant's Tools |
| 8 | "Tool update failed" on phone number | Not E.164 format | Use `+15082827112` (with + and country code) |
| 9 | Server URL pointing to wrong platform | Was still pointing to Make | Update to n8n production webhook URL |
| 10 | Streamlit blocked by security app | Runs local web server | Switched to Tkinter desktop app |
| 11 | getpass won't accept paste on Windows | Terminal limitation | Changed to `input()` instead |
| 12 | Duplicate articles in Supabase | Accidentally uploaded twice | `DELETE FROM documents WHERE id > 163;` (or whatever the cutoff) |

---

## Useful SQL Commands

```sql
-- Count all articles
SELECT COUNT(*) FROM documents;

-- See all articles with filenames
SELECT id, metadata->>'filename' as filename FROM documents ORDER BY id;

-- Delete duplicates above a certain ID
DELETE FROM documents WHERE id > 163;

-- Test similarity search
SELECT id, metadata->>'filename', 1 - (embedding <=> (SELECT embedding FROM documents WHERE id = 155)) as similarity
FROM documents ORDER BY similarity DESC LIMIT 10;
```

---

## Test Questions

**KB Questions (should return answers):**
1. "How do I reset my Windows password?"
2. "How do I set up my company email on my iPhone?"
3. "How do I connect to the VPN?"
4. "How do I set up MFA?" (new article)
5. "My printer is offline" (new article)
6. "My Outlook won't open" (new article)
7. "How do I set up out of office?" (new article)
8. "How do I clear my browser cache?"
9. "My computer is running really slow"
10. "Is Dave Hynes technical?" (Fun - answer is NO!)

**Escalation Test (should transfer call):**
11. "Who is the President of the United States?" (not in KB, triggers transfer)

---

## Pending/TODO Items

1. **Email Summary Workflow** - n8n webhook created, VAPI tool configured, but Gmail node needs support@tactivai.com password from Dave
2. **GitHub Release** - Upload TactivAI-KB-Upload.exe as v1.0.0 release at github.com/TonkaStinks/TactivAI-KB-Upload-Tool/releases
3. **Future: PDF Ingestion** - When handed PDF help files, use `pymupdf4llm` to convert to markdown, chunk by section (~500-800 tokens with overlap), embed each chunk separately
4. **Future: Chunking** - Current articles are embedded whole. For longer content, split into chunks per section for more precise search results

---

## How to Add New Articles

### Using the Upload App (Recommended)
1. Create `.md` files following the article format above
2. Put them in a folder
3. Run `upload_app.py` (or `TactivAI-KB-Upload.exe`)
4. Browse to the folder, enter creds, click Upload

### Using the Generator + Upload
1. Add article definitions to `generate_articles.py` ARTICLES list
2. Run `python generate_articles.py` (enter OpenAI key when prompted)
3. Run `upload_app.py`, point to the appropriate `generated-articles/` subfolder
4. Upload with correct category tag

---

## Python Dependencies

```bash
pip install openai httpx
# For building exe:
pip install pyinstaller
```

---

## Quick Start (for new machine)

1. Clone: `git clone https://github.com/TonkaStinks/TactivAI-KB-Upload-Tool.git`
2. Install: `pip install openai httpx`
3. Run upload tool: `python upload_app.py`
4. Run article generator: `python generate_articles.py`
5. Build exe: `pyinstaller --onefile --windowed --name "TactivAI-KB-Upload" upload_app.py`