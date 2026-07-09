# Product Info Telegram Bot for AI-Powered Expiry Date Validation

A Telegram-based product information assistant built with **n8n**, **FastAPI**, **OpenAI**, and **Open Food Facts**. The workflow lets users search product details, ask expiry/product questions, and manage product records directly from Telegram while connecting to the expiry-date validation backend.

This bot is part of the larger **AI-Powered Expiry Date Validation** system for retail, warehouse, and dark-store inventory operations. The full project combines barcode lookup, OCR-assisted label scanning, inventory intake, expiry alerts, manual review workflows, and a dashboard UI.

---

## What this workflow does

The n8n workflow listens for Telegram messages, routes commands, calls the backend or Open Food Facts, formats the response, and sends a clean reply back to the user.

Core capabilities:

- Product lookup by barcode, product name, ID, or SKU.
- Product question answering through the backend `/api/v1/products/ask` endpoint.
- Product category search.
- Product removal with confirmation.
- Product edit/update command flow.
- Open Food Facts lookup by barcode or product name.
- OpenAI-powered product assistant for natural-language product questions.
- Conversation memory for short follow-up context.
- Fallback replies when the backend or AI lookup fails.

---

## n8n Workflow Overview

Click the image below to open it in full size. After opening, use your browser zoom controls or trackpad pinch zoom to inspect each node clearly.

<a href="assets/n8n-workflow.png" target="_blank">
  <img src="assets/n8n-workflow.png" alt="n8n Product Info Telegram Bot workflow" width="100%" />
</a>

> **Zoom tip:** On GitHub, click the workflow image to open it, then use `Ctrl + +` / `Ctrl + -` on Windows/Linux or `Cmd + +` / `Cmd + -` on macOS.

---

## High-Level Architecture

```text
Telegram User
  -> Telegram Trigger in n8n
  -> Parse Telegram Message
  -> Route Command
      -> /start and /help replies
      -> /product backend product search
      -> /ask backend product question answering
      -> /category backend category search
      -> /remove backend product deletion with confirmation
      -> /edit backend product update
      -> unknown messages / AI product assistant path
  -> Format Response
  -> Send Telegram Reply
```

The wider application stack works like this:

```text
Next.js Frontend
  -> FastAPI backend on port 8001
  -> PostgreSQL database on port 5434

Telegram Bot via n8n
  -> FastAPI backend product APIs
  -> Open Food Facts public product APIs
  -> OpenAI model node for natural-language product support
```

---

## Main n8n Nodes

| Node | Purpose |
| --- | --- |
| `Telegram Trigger` | Receives Telegram messages. |
| `Config` | Stores the backend base URL used by API request nodes. |
| `Parse Telegram Message` | Extracts chat ID, user ID, username, command, and argument. |
| `Route Command` | Routes `/start`, `/help`, `/product`, `/ask`, unknown messages, and other command branches. |
| `Product Search Request` | Calls the backend product search API. |
| `Ask Backend Request` | Sends product-related questions to the backend. |
| `Category Search Request` | Searches backend products by category. |
| `Remove Product Request` | Deletes a product after confirmation. |
| `Edit Product Request` | Updates product fields through the backend. |
| `Product Info Agent` | Uses an OpenAI chat model and tools for natural-language product support. |
| `Search Open Food Facts By Barcode` | Looks up product data by barcode. |
| `Search Open Food Facts By Name` | Looks up product data by product name. |
| `Conversation Memory` | Keeps short conversation context for follow-up questions. |
| `Send Telegram Reply` | Sends final replies to Telegram. |
| `Send Fallback Reply` | Sends a safe error message when processing fails. |

---

## Telegram Commands

### `/start`

Shows the welcome message and basic usage examples.

```text
/start
```

### `/help`

Shows available commands and examples.

```text
/help
```

### `/product`

Looks up a product using barcode, name, ID, or SKU.

```text
/product 8901262010011
/product Amul Milk
/product AMUL-TAAZA-500ML
```

The workflow calls:

```text
GET /api/v1/products/search
```

with query parameters such as:

```text
query=<user input>
request_source=TELEGRAM
requested_by=<telegram username>
```

### `/ask`

Asks a product-related question and returns a focused answer.

```text
/ask What is the expiry date of Amul Milk?
/ask Show ingredients of 8901262010011
/ask Is Amul Milk expired?
```

The workflow calls:

```text
POST /api/v1/products/ask
```

Example supported intents include:

- Expiry date
- Manufacturing date
- Batch number
- Ingredients
- Nutrition
- Storage instruction
- Product status
- General product details

### `/category`

Searches products by category.

```text
/category Dairy
/category Spices
/category Beverages
```

The workflow calls:

```text
GET /api/v1/products/category
```

### `/remove`

Removes a product record only after explicit confirmation.

Step 1: request deletion.

```text
/remove 8901262010011
```

Step 2: confirm deletion.

```text
/remove 8901262010011 confirm
```

The workflow calls:

```text
DELETE /api/v1/products/delete
```

### `/edit`

Updates selected product fields.

```text
/edit 8901262010011 price=45
/edit AMUL-TAAZA-500ML category=Dairy
```

Editable fields:

```text
name, brand, category, sku, barcode, price, ingredients, storage_instruction, description
```

---

## AI Product Assistant Behavior

The workflow includes an AI product assistant that can answer natural-language product questions. It uses:

- `OpenAI Model`
- `Conversation Memory`
- `Search Open Food Facts By Barcode`
- `Search Open Food Facts By Name`

Expected user messages include:

```text
8901262010011
Maggi noodles
What are the ingredients of Maggi noodles?
Is this healthy?
```

The assistant is designed to respond with concise Telegram Markdown sections such as:

```text
*Product name*
Brand, category

*Ingredients*
Ingredient list

*Nutrition (per 100g)*
Energy, protein, fat, sugar

*Health assessment*
Short nutrition-based summary
```

---

## Backend Requirements

The workflow expects the active backend to expose these APIs:

| Feature | Method | Endpoint |
| --- | --- | --- |
| Product search | `GET` | `/api/v1/products/search` |
| Product Q&A | `POST` | `/api/v1/products/ask` |
| Category search | `GET` | `/api/v1/products/category` |
| Product delete | `DELETE` | `/api/v1/products/delete` |
| Product edit | `PUT` or configured backend method | Product edit endpoint used by `Edit Product Request` |

Update the `Config` node in n8n with your backend URL:

```text
backend_base_url=https://your-backend-url.example.com
```

For local development, this usually points to a tunnel such as ngrok or Cloudflare Tunnel if Telegram/n8n needs public HTTPS access.

---

## Environment and Credentials

Before running the workflow, configure these credentials in n8n:

| Credential | Used by |
| --- | --- |
| Telegram Bot API credential | Telegram Trigger and Telegram reply nodes |
| OpenAI API credential | OpenAI Model node |
| Backend public URL | `Config` node |

Do not commit real secrets, bot tokens, API keys, or production tunnel URLs to the repository.

---

## Importing the Workflow into n8n

1. Open n8n.
2. Go to **Workflows**.
3. Select **Import from File**.
4. Import `workflow/Product Info Telegram Bot.json`.
5. Reconnect the Telegram and OpenAI credentials.
6. Open the `Config` node and replace `backend_base_url` with your backend URL.
7. Save the workflow.
8. Activate the workflow.
9. Test from Telegram using `/start` and `/help`.

---

## Running the Active Full-Stack App Locally

Start PostgreSQL and pgAdmin:

```bash
cd backend_v2
docker compose up -d
```

Create `backend_v2/.env`:

```env
DATABASE_URL=postgresql://expiry_user:expiry_pass@localhost:5434/expiry_db
APP_ENV=development
APP_VERSION=2.0.0
SECRET_KEY=change_this_secret_key_phase2
UPLOAD_DIR=./uploads
ML_WEBHOOK_URL=
```

Start the FastAPI backend:

```bash
cd backend_v2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Create `Frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
NEXT_PUBLIC_SCAN_URL=http://localhost:8001/api/scan
```

Start the frontend:

```bash
cd Frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## Public Tunnel Setup for Telegram/n8n Testing

Telegram webhooks and remote n8n workflows often need a public HTTPS backend URL. You can expose the backend using ngrok:

```bash
ngrok http 8001
```

Then update the n8n `Config` node:

```text
backend_base_url=https://your-ngrok-url.ngrok-free.app
```

If using ngrok, the workflow already includes the `ngrok-skip-browser-warning` header in backend HTTP request nodes.

---

## Error Handling

The workflow includes safe responses for common failure states:

- Missing command arguments.
- Unsupported commands.
- Product not found.
- Invalid question.
- Backend temporarily unavailable.
- AI/product lookup service unavailable.
- Deletion without confirmation.
- Edit command with invalid field format.

The bot avoids exposing raw technical errors, status codes, or stack traces to Telegram users.

---

## Recommended Repository Layout

```text
.
|-- Frontend/                         Next.js dashboard frontend
|-- backend_v2/                       Active FastAPI backend
|-- backend/                          Original backend kept for reference
|-- api/                              Legacy OCR API
|-- pipeline/                         OCR/date parsing prototype
|-- demo/                             Streamlit and desktop scanner demos
|-- workflow/
|   |-- Product Info Telegram Bot.json
|-- assets/
|   |-- n8n-workflow.png
|-- README.md
```

---

## Testing Checklist

Use this checklist after importing the workflow:

- [ ] Telegram bot credential is connected.
- [ ] OpenAI credential is connected.
- [ ] `backend_base_url` points to the correct public backend URL.
- [ ] Backend health endpoint works.
- [ ] `/start` returns the welcome message.
- [ ] `/help` returns command instructions.
- [ ] `/product <barcode>` returns product data or a clean not-found message.
- [ ] `/ask <question>` returns a product-related answer.
- [ ] `/category <name>` returns matching products.
- [ ] `/remove <identifier>` asks for confirmation before deleting.
- [ ] `/edit <identifier> field=value` updates product data correctly.

---

## Troubleshooting

### Telegram messages do not trigger the workflow

Check that the workflow is active, the Telegram credential is valid, and no other workflow is using the same bot webhook.

### Backend requests fail

Confirm that the backend is running and that the `Config` node uses a public HTTPS URL when n8n is not running on the same machine.

### Product lookup returns not found

Check whether the barcode, SKU, or product name exists in the backend database. For Open Food Facts lookup, try a barcode or a more specific product name.

### Markdown formatting breaks in Telegram

Check the parse mode in the Telegram reply node. The workflow uses both `Markdown`, `MarkdownV2`, and `HTML` in different branches, so formatting must match the escaping logic in the corresponding formatter node.

### Camera or OCR features do not work in the frontend

Allow browser camera permissions, improve lighting, avoid glare, and use HTTPS when testing from another device.

---

## Security Notes

- Replace all development secrets before production deployment.
- Do not commit `.env`, `.env.local`, API keys, Telegram tokens, OpenAI keys, database dumps with sensitive data, or production tunnel URLs.
- Restrict CORS before deploying publicly.
- Add authentication/authorization checks for destructive backend actions such as product deletion and editing.
- Keep confirmation flows for delete operations.

---

## License

Add your project license here.
