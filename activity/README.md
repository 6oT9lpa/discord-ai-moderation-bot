# Omnibot Discord Activity

This folder contains the Discord Activity control panel for OmniBot.

The Activity is a Vue 3 frontend loaded inside Discord and a FastAPI backend that handles OAuth code exchange, RBAC checks, Discord API access, settings persistence, and Activity audit logging. Protected workspace routes are intended to work inside Discord only.

## Structure

- `client/` - Vue 3 + Vite + TypeScript frontend loaded inside Discord.
- `server/` - FastAPI backend for OAuth, session building, RBAC, bot settings, logs, Dev Blog, welcome, stats, voice rooms, and Discord reference data.

## Access Model

Activity access is not the same thing as Discord server roles. Discord roles are synchronized into OmniBot, then mapped to Activity access roles.

Built-in Activity roles:

- `user`;
- `creator`;
- `developer`;
- `moderator`;
- `administrator`.

Rules:

- users must open the panel from a Discord server Activity launch;
- if Discord roles are not synchronized, users receive `403`;
- Discord server administrators can synchronize roles with `/sync_roles` or the Activity sync action;
- tabs are hidden when the user's Activity role has no permission for that module;
- `administrator` Activity role permissions cannot be changed.

The frontend waits for module data before rendering each panel. Heavy panels use aggregated backend endpoints:

- `/api/activity/rbac/access-control`;
- `/api/activity/rbac/role-panels`;
- `/api/bot/settings`.

This avoids partial tables and reduces Discord OAuth rate-limit pressure.

## Developer Portal Setup

1. Open the Discord Developer Portal for the OmniBot application.
2. Enable Activities for the app.
3. Add the Activity URL Mapping that points to the public HTTPS URL serving this FastAPI app.
4. Keep the application as a confidential client for this deployment. Do not enable Public Client.
5. Use the bot invite URL scopes `bot` and `applications.commands`.

The Activity SDK authorization uses these scopes in code:

- `identify`;
- `guilds`;
- `applications.commands`.

## Local Run

Create `activity/client/.env` and set:

```env
VITE_DISCORD_CLIENT_ID=your_discord_application_client_id
VITE_API_BASE_URL=
```

Start the backend:

```bash
python -m uvicorn activity.server.main:app --host 0.0.0.0 --port 8008 --reload
```

Start the frontend:

```bash
cd activity/client
npm install
npm run dev
```

For local UI work, Vite proxies `/api` to `http://localhost:8008`. For production, leave `VITE_API_BASE_URL` empty so the built frontend calls the same origin with `/api/...`.

## Required Server Env

The backend reads the existing project `.env` and also needs:

```env
DISCORD_CLIENT_ID=your_discord_application_client_id
DISCORD_CLIENT_SECRET=your_discord_oauth_client_secret
DISCORD_PROXY_URL=http://127.0.0.1:10809
```

`DISCORD_PROXY_URL` is required when the host cannot reach Discord directly. The current production setup uses an HTTP proxy provided by the local VLESS/Xray client.

## Production Services

The current systemd services are:

- `omnibot-bot`;
- `omnibot-activity`;
- `xray-client`.

`omnibot-bot` and `omnibot-activity` should start after `xray-client` when Discord traffic must go through the VLESS route.

## Current Panels

- Dashboard - module overview and recent Activity audit events.
- Access Control - Activity roles and tab permissions.
- Welcome Alerts - welcome embed settings, reset, and test send.
- Role Panels - synchronized Discord roles mapped to Activity roles.
- Dev Blog - up to 10 embeds, publish, and up to 10 drafts.
- Logs - server logs and Activity audit changes.
- Server Stats - statistics available from the bot API.
- Voice Rooms - administrator/moderator room management and user-owned room controls.
- Bot Settings - channel purposes, role purposes, sync roles, welcome toggle, and bot runtime settings.
- Integrations and Health Status - current integration and service health surfaces.

Discord snowflake IDs must be treated as strings in the frontend. Do not convert guild, channel, role, message, or user IDs to JavaScript `number`.
