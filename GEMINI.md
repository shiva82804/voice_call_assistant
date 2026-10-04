# Security & Privacy Guidelines for AI Agents

## Mandatory Privacy Rules
1. **STRICT PROHIBITION**: NEVER view, read, open, search, grep, edit, display, or leak the contents of `.env` or any file matching `*.env*` (except `.env.example`).
2. **Confidentiality of Secrets**: Treat all environment variables, API tokens (Vapi, Twilio, Meta, OpenAI), passwords, private keys, and webhook credentials as confidential secrets.
3. **Reference Only `.env.example`**: When assisting the user with environment setup, variables, or configuration, refer exclusively to `.env.example` or explain parameters conceptually. Never attempt to read or print live values from `.env`.
4. **Tool Access Restriction**: If any tool call would read or output secrets from `.env`, do not make that tool call.
