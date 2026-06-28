# OmniBot Knowledge Base

**Last Updated:** June 28, 2026

This knowledge base helps server administrators, moderators, and members understand what OmniBot can do, how to configure it, and how to solve common issues.

> Available commands depend on the Bot version, granted Discord permissions, and modules enabled on a specific server.

## 1. What the Bot Does

OmniBot is a bot for managing Discord servers. It helps automate roles, moderation, logging, statistics, welcome messages, dynamic voice rooms, stream announcements, Dev Blog publishing, and Activity-based administration.

The core idea of the project is to provide a complete server administration toolkit with SQLite persistence and AI moderation powered by self-hosted Ollama.

## 2. Main Modules

### Roles and Autoroles

The roles module can:

- automatically assign a base role to new members;
- create role panels with buttons;
- use emoji/reactions for role assignment;
- add and remove roles from a panel without rebuilding the whole server setup;
- show a list of server roles;
- prevent assigning roles above the Bot's role in the Discord hierarchy.

Useful commands:

```text
/role-panel setup #channel
/role-panel add @role
/role-autoassign set @role
/roles-list
```

### Discord Activity Control Panel

The Activity panel is the in-Discord workspace for server administration. It should be opened from Discord, not from a standalone browser tab.

Core behavior:

- Discord roles are synchronized into OmniBot;
- synchronized Discord roles are mapped to Activity access roles;
- tabs are hidden when the user has no permission for that module;
- the workspace waits for module data before showing a panel;
- Discord snowflake IDs are handled as strings in the frontend.

Built-in Activity roles:

- `user`;
- `creator`;
- `developer`;
- `moderator`;
- `administrator`.

The `administrator` Activity role always has full module access and cannot be edited from the Access Control table.

Default modules visible to all configured users:

- Dashboard;
- Integrations;
- Health Status;
- Server Stats;
- Voice Rooms.

Administrator modules:

- Access Control;
- Welcome Alerts;
- Role Panels;
- Dev Blog;
- Logs;
- Bot Settings.

Setup flow:

```text
1. Invite the bot with bot + applications.commands scopes.
2. Open the Activity from a Discord server.
3. Run /sync_roles or press Sync roles as a Discord server administrator.
4. Open Access Control and configure module permissions.
5. Open Role Panels and map synchronized Discord roles to Activity roles.
```

### Welcome and Member Events

The welcome module is used to greet new members and log member joins/leaves.

Features:

- enable or disable welcome messages;
- configure title, description, color, and embed images;
- add buttons for rules and roles channels;
- preview the welcome message;
- reset welcome settings.

Example commands:

```text
/welcome setup
/welcome toggle
/welcome preview
/welcome config
/welcome reset
```

The Activity panel exposes this module as **Welcome Alerts**. Rules channel and roles channel dropdowns are loaded from live Discord text channels.

### Moderation

The moderation module helps moderators apply actions quickly and keep violation history.

Features:

- warnings;
- mutes and unmutes;
- kicks;
- bans and unbans;
- user history;
- active punishment list;
- message cleanup;
- channel slowmode.

Example commands:

```text
/warn @user reason
/mute @user 10m reason
/unmute @user
/kick @user reason
/ban @user reason
/unban user_id
/history @user
/punishments list
/purge 50
/slowmode #channel 5
```

### AI Moderation

AI moderation analyzes messages and helps detect spam, advertisements, invites, NSFW content, bullying, and dangerous content.

The project is designed for self-hosted Ollama. This means the model runs on the Bot owner's infrastructure rather than through an external commercial AI API, unless the configuration is changed separately.

Review categories:

- `SPAM`
- `ADVERTISEMENT`
- `INVITE`
- `VIOLENCE`
- `BULLYING`
- `NSFW`
- `SAFE`

Example commands:

```text
/ai-stats
/ai-whitelist add #channel
/ai-whitelist remove #channel
/ai-threshold set 0.85
/ai-review message_id
```

Important: AI can make mistakes. Serious punishments should be reviewed by a human moderator.

### Logging

The Bot can audit server events and store data in SQLite.

Events that may be logged:

- regular messages;
- deleted messages;
- edited messages;
- bulk message deletion;
- member joins and leaves;
- role and nickname changes;
- channel creation, deletion, and updates;
- role creation, deletion, and updates;
- voice channel joins and leaves;
- punishments and moderator actions.

Default message log retention is **30 days**, unless changed with `MESSAGE_LOG_RETENTION_DAYS`.

### Statistics

The statistics module shows server and user activity.

Features:

- server statistics for a period;
- statistics for a specific user;
- top active members;
- top active channels;
- message activity;
- voice channel activity.

Example commands:

```text
/stats server
/stats user @user
/stats channels
/stats activity
/leaderboard
```

### Dynamic Voice Rooms

The voice room module lets members create temporary rooms through a special trigger channel.

Features:

- create a private room;
- rename the room;
- set a user limit;
- lock or unlock the room;
- invite a user;
- kick a user from the room;
- transfer room ownership;
- automatically delete an empty temporary room.

Example commands:

```text
/room name "My Room"
/room limit 5
/room lock
/room unlock
/room invite @user
/room kick @user
/room transfer @user
```

### Streams and Auto-Publications

The streams module is used for automatic Twitch, YouTube, Kick, and other platform announcements when integrations are configured.

Features:

- add a streamer;
- remove a streamer;
- show the streamer list;
- configure an announcement template;
- set a role to ping;
- automatically publish stream start announcements;
- prevent duplicate announcements.

Example commands:

```text
/streamer add twitch https://twitch.tv/nick
/streamer remove twitch nick
/streamer list
/stream-template set
/subscribe youtube channel_id
```

### Dev Blog

Dev Blog helps publish development news and project updates in a clean embed format from the Activity panel.

Features:

- build up to 10 embeds;
- keep the first embed locked so at least one embed remains;
- add title, content, image URLs, and colors;
- publish to the configured Dev Blog channel;
- save up to 10 drafts in SQLite;
- load saved drafts from the bottom of the page.

Example commands:

```text
Activity -> Dev Blog -> Publish
Activity -> Dev Blog -> Save Draft
Activity -> Bot Settings -> Dev Blog channel
```

If publishing fails, check that the Dev Blog channel purpose is configured and that the Activity is using the exact Discord guild ID. Discord IDs must not be rounded or converted to JavaScript numbers.

### Bot Settings

Bot Settings visualizes command-style setup in one Activity page.

Current surfaces:

- welcome toggle;
- runtime settings such as command prefix, activity name, status, and log level;
- List Channels dropdowns for welcome, logs, stream alerts, Dev Blog, and admin logs;
- List Roles dropdowns for Activity admin, creator, and developer role purposes;
- Sync roles action.

The page loads channels, roles, channel purposes, and role purposes through one aggregated backend response. If dropdowns are empty, check backend logs for Discord API errors and verify the bot can reach Discord through its proxy.

### Access Control

Access Control manages Activity roles and tab permissions.

Actions:

- add a unique Activity role by entering its name and pressing Add role;
- delete custom roles from the rightmost table column;
- choose `access` or `deny` per module cell;
- save changes automatically.

The built-in roles are:

- User;
- Creator;
- Developer;
- Moderator;
- Administrator.

Administrator permissions are immutable.

### Role Panels

Role Panels maps synchronized Discord roles to Activity roles.

Steps:

```text
1. Run /sync_roles or use Sync roles.
2. Open Role Panels.
3. Find the Discord role row.
4. Check one or more Activity roles for that Discord role.
5. Changes save immediately.
```

If synchronized roles do not appear, confirm `activity_synced_roles` contains rows for the server and that the Activity panel has been reopened after deployment.

## 3. Quick Server Setup

### Minimum Bot Permissions

For basic operation, the Bot usually needs:

- View Channels;
- Send Messages;
- Embed Links;
- Use Slash Commands;
- Manage Roles;
- Manage Messages;
- Moderate Members;
- Read Message History;
- Connect;
- Move Members, if voice rooms are used.

Some features may need additional permissions. Do not grant `Administrator` if precise permissions are enough.

### Bot Role

The Bot's role must be above the roles it assigns or removes. If the Bot cannot assign a role, the most common cause is Discord role hierarchy.

### Recommended Channels

A practical server structure can include:

- `#rules`
- `#roles`
- `#welcome`
- `#general`
- `#logs`
- `#deleted-messages`
- `#punishments`
- `#bot-config`
- `#stream-announcements`
- `#dev-blog`
- voice channel `+ Create Room`

## 4. `.env` Configuration

Main environment variables:

```env
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=123456789012345678
DISCORD_OWNER_ID=123456789012345678
DATABASE_URL=sqlite:///data/nexsusguard.db
DISCORD_PROXY_URL=http://127.0.0.1:10809

AUTO_ROLE_ID=123456789012345678
LOG_CHANNEL_ID=123456789012345678
WELCOME_CHANNEL_ID=123456789012345678

LOG_LEVEL=INFO
MESSAGE_LOG_RETENTION_DAYS=30
PUNISHMENT_RETENTION_DAYS=365
RETENTION_CLEANUP_INTERVAL_HOURS=6
DISCORD_CLIENT_ID=your_discord_application_client_id
DISCORD_CLIENT_SECRET=your_discord_oauth_client_secret
```

If streams or external APIs are used, you may also need:

```env
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
```

For `activity/client/.env`:

```env
VITE_DISCORD_CLIENT_ID=your_discord_application_client_id
VITE_API_BASE_URL=
```

Leave `VITE_API_BASE_URL` empty for production builds. The Activity frontend should call `/api/...` on the same origin.

## 5. Data Storage

The Bot uses SQLite. The database may store:

- server settings;
- channel settings;
- roles and role panels;
- welcome configuration;
- message logs;
- server events;
- punishment history;
- user statistics;
- server statistics;
- voice rooms and voice sessions;
- stream and publication settings.
- Activity access roles and module permissions;
- synchronized Discord role metadata;
- Dev Blog drafts and publish records;
- Activity audit events.

See the [Privacy Policy](./PRIVACY_POLICY.md) for more details.

## 6. FAQ

### The Bot Does Not Respond to Slash Commands

Check that:

- the Bot is online;
- slash commands are synced;
- the Bot has `Use Slash Commands`;
- the command is available in this channel;
- the command module loaded without errors.
- the bot can reach Discord directly or through `DISCORD_PROXY_URL`.

### The Activity Shows `Session failed`

Check that:

- the Activity is opened inside Discord;
- `VITE_DISCORD_CLIENT_ID` matches the Discord application;
- `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` are configured on the server;
- the Discord application is not configured as Public Client for this backend-exchange flow;
- production frontend was built with empty `VITE_API_BASE_URL`;
- `omnibot-activity` is running and listening on the configured port.

### Activity Returns `403`

Common causes:

- Discord roles have not been synchronized;
- the user has no mapped Activity role;
- the target tab is denied for the user's Activity role;
- the user is opening the Activity from the wrong server;
- the guild ID was rounded by frontend code.

Discord snowflake IDs are larger than JavaScript's safe integer range. Treat guild IDs, role IDs, channel IDs, user IDs, and message IDs as strings in frontend code.

### Activity Returns `429 Too Many Requests`

This usually means too many Discord OAuth/member requests were triggered at once.

Check that:

- the current frontend uses aggregated endpoints for Access Control, Role Panels, and Bot Settings;
- the backend access-context cache is active;
- users are not repeatedly refreshing the Activity during Discord rate limits;
- Discord API traffic goes through the configured proxy when direct access is blocked.

### Role Panels Do Not Show Roles

Check that:

- `/sync_roles` completed successfully;
- `activity_synced_roles` has rows for the current server;
- the user has administrator Activity access;
- the frontend is using `/api/activity/rbac/role-panels`;
- the Activity iframe is not using a cached old JS asset.

### Access Control Does Not Show Built-In Roles

Check that:

- the Activity backend has initialized the database;
- opening Access Control calls `/api/activity/rbac/access-control`;
- the built-in roles exist: User, Creator, Developer, Moderator, Administrator;
- the user has Activity administrator access.

### Dev Blog Says `User is not a member of this guild`

This usually means the request used a rounded guild ID.

Fix checklist:

- reopen the Activity to load the latest frontend asset;
- ensure Dev Blog requests send the session guild ID as a string;
- do not pass `Number(guildId)` from frontend code;
- confirm the request guild ID matches the server ID from the Activity URL.

### The Bot Cannot See Messages

Check in the Discord Developer Portal:

- `MESSAGE CONTENT INTENT` is enabled;
- `SERVER MEMBERS INTENT` is enabled if member events are needed;
- the Bot has `View Channels` and `Read Message History`;
- the channel is not excluded from AI moderation or logging.

### The Bot Does Not Assign a Role

Check that:

- the Bot has `Manage Roles`;
- the Bot's role is above the target role;
- the role is not a managed role from another application;
- the role ID is correct;
- the role panel is active.

### The Bot Does Not Write Logs

Check that:

- `LOG_CHANNEL_ID` is set;
- the Bot can see the log channel;
- the Bot has `Send Messages` and `Embed Links`;
- the logging module is registered;
- the database is writable.

### AI Moderation Does Not Work

Check that:

- Ollama is running;
- the model is downloaded;
- `OLLAMA_HOST` points to the correct address;
- the server has enough RAM;
- the channel is not whitelisted;
- the `ai-threshold` value is not too high.

Commands to check Ollama:

```bash
ollama list
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"Hello"}'
```

### The Database Shows `database is locked`

SQLite may lock when too many operations happen at the same time.

Try:

```sql
PRAGMA journal_mode=WAL;
```

Also check that multiple Bot instances are not using the same SQLite database at the same time.

### A Voice Room Is Not Deleted

Check that:

- the room is actually empty;
- the Bot has permission to manage the channel;
- the channel was created by the Bot as a temporary room;
- the voice module is loaded;
- there are no errors in the logs.

## 7. Administrator Recommendations

- Test the Bot on a separate test server first.
- Do not grant `Administrator` if precise permissions are enough.
- Restrict access to log channels.
- Tell members that logging and AI moderation are enabled.
- Configure log retention.
- Back up the SQLite database.
- Review disputed AI detections manually.
- Keep `.env` out of public access.

## 8. Moderator Recommendations

- Provide a clear reason for each punishment.
- Check user history before serious sanctions.
- Do not publish log contents in public channels.
- Use mute before ban when the violation is not critical.
- Check Bot permissions before bulk actions.
- If AI moderation makes a false detection, remove the punishment and adjust the threshold.

## 9. Useful Project Links

- [Privacy Policy](./PRIVACY_POLICY.md)
- [Terms of Service](./TERMS_OF_SERVICE.md)
- [Project README](../readme.md)
- [Discord Terms](https://discord.com/terms)
- [Discord Privacy Policy](https://discord.com/privacy)

## 10. Support Response Templates

### Data Deletion Request

```text
Hello! To delete data, please send your Discord user ID and the server ID where the Bot was used. We will review the request and delete the data we can remove without compromising server safety or moderation history.
```

### Punishment Appeal

```text
Hello! Please provide your Discord user ID, the server, the punishment date, and the reason shown by the Bot. Moderators will review the history and logs, then make a decision.
```

### False AI Detection

```text
Thanks for reporting this. Please send the message link or message ID if available. We will review the AI category, moderation threshold, and update whitelist or settings if needed.
```

### Bot Is Not Working

```text
Please check that the Bot is online, has the required permissions, can see the channel, and that the command module is loaded. If the problem remains, send the command name, server ID, channel, and time of the error.
```
