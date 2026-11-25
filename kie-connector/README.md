# Betty's Kie.ai connector for Claude

A small private connector that lets Claude make images and videos with your Kie.ai account. It runs free on Cloudflare Workers. You only pay for the Kie.ai credits you use.

**Your Kie.ai key never goes in a chat, in this repo, or in Claude.** It lives only in Cloudflare as a secret.

## What Claude can do with it

| Tool | What it does | Costs credits? |
|---|---|---|
| `create_image` | Makes an image. Can use your reference photos to keep faces and places consistent. Nano Banana 2 (default, cheapest good result), Nano Banana Pro, or Seedream edit. | Yes |
| `create_video` | Turns a still image into a short video. Kling 2.1 Standard (default, 720p, fewest credits), Kling 2.6, or Google Veo 3.1. | Yes, more than images |
| `check_task` | Checks whether a shot is done and gives the link. | No |
| `upload_reference_image` | Puts a reference photo where Kie.ai can see it (lasts 24 hours). | No |
| `get_credits` | Shows your Kie.ai balance. | No |
| `create_task_advanced` | Any other Kie.ai model, using the exact settings from docs.kie.ai. | Yes |

**Micro drama defaults:** 9:16, 720p (1K for images), 5-second clips, no audio, cheapest good model. No clip can be longer than 17 seconds.

Kie.ai deletes finished images and videos after 14 days, so save the ones you keep to Google Drive.

## One-time setup (about 10 minutes)

### Step 1. Make up a connector password
Make up a long password of **at least 20 letters and numbers, no spaces or symbols** (for example, mix three words and a number). Keep it in your password manager. It goes in the connector link, so anyone with the full link could use your credits. Never post the full link anywhere.

### Step 2. Put the connector on Cloudflare (free)
1. Go to **dash.cloudflare.com** and sign up for a free account (or sign in).
2. In the left menu, open **Compute (Workers)**, then **Workers & Pages**. Click **Create**.
3. Choose **Import a repository** and connect your GitHub. Pick **Bettys-Soul-System**.
4. On the setup screen, set **Project name** to `betty-kie-connector`. Open **Advanced settings** and set **Root directory** (path) to `kie-connector`. Leave the other settings as they are.
5. Click **Create and deploy**. Wait for the green "Success".

### Step 3. Add your two secrets in Cloudflare
1. Open the `betty-kie-connector` worker, then **Settings**, then **Variables and Secrets**. Click **Add**.
2. Type: **Secret**. Name: `KIE_API_KEY`. Value: your key from **kie.ai/api-key**. Click **Deploy**.
3. Click **Add** again. Type: **Secret**. Name: `CONNECTOR_PASSWORD`. Value: the password from Step 1. Click **Deploy**.

### Step 4. Find your connector link
On the worker's main page, copy the address that ends in `.workers.dev` (for example `https://betty-kie-connector.yourname.workers.dev`). Open it in your browser; it should say "Betty's Kie.ai connector is running."

Your connector link is that address plus `/mcp/` plus your password:

```
https://betty-kie-connector.yourname.workers.dev/mcp/YOUR-PASSWORD
```

### Step 5. Add it to Claude
1. In Claude, go to **Settings**, then **Connectors**, then **Add custom connector**.
2. Name: `Kie.ai`. URL: your connector link from Step 4. Leave the advanced (OAuth) fields empty. Click **Add**.
3. In a new chat, turn on the Kie.ai connector from the tools menu and ask: "Check my Kie.ai credits." If it shows your balance, you're connected.

## If something goes wrong
- **"Not found"**: the password in the link doesn't match `CONNECTOR_PASSWORD` exactly.
- **"Setup needed"**: one of the two secrets is missing in Cloudflare.
- **"key was refused"**: re-copy the key from kie.ai/api-key into `KIE_API_KEY`.
- **"Not enough Kie.ai credits"**: top up at kie.ai.
- **To shut it off fast**: delete the key at kie.ai/api-key, or change `CONNECTOR_PASSWORD` in Cloudflare.

## For developers
- `src/index.js` is a stateless MCP server (Streamable HTTP, JSON responses, no dependencies).
- `npm test` runs the tests with a mocked Kie.ai.
- Kie.ai API docs: https://docs.kie.ai
