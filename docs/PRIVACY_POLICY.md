# Privacy Policy for OmniBot

**Effective Date:** June 18, 2026  
**Last Updated:** June 18, 2026

This Privacy Policy explains what data **OmniBot** ("the Bot", "we", "our service") processes, why it is needed, how long it is stored, and how deletion can be requested.

The Bot operates inside Discord servers and uses the Discord API. By using the Bot on a server, you also continue to follow the [Discord Terms of Service](https://discord.com/terms), [Discord Privacy Policy](https://discord.com/privacy), [Discord Developer Terms](https://support-dev.discord.com/hc/en-us/articles/8562894815383-Discord-Developer-Terms-of-Service), and [Discord Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy).

## 1. Data Controller

Bot operator: **6oT9lpa / OmniBot project team**.  
Privacy contact: **[Discord Support Server](https://discord.gg/wUb3Js2wzt)**.  
Discord owner ID / responsible administrator: **[\[Owner Discord ID\]](https://discord.gg/wUb3Js2wzt)**.

If the Bot is installed on your Discord server, that server's administrators are also responsible for choosing the settings: which modules are enabled, which channels are logged, which roles are assigned automatically, and who can access moderation logs.

## 2. Information We Collect

The Bot collects only the data needed for enabled features. If a module is not enabled or configured on a server, the related data may not be collected.

### 2.1. Server Data

The Bot may store:

- Discord server ID;
- channel IDs selected for logs, welcome messages, roles, statistics, stream announcements, and other features;
- role IDs, names, colors, and positions;
- channel settings such as AI-moderation whitelist, slowmode, custom names, and channel purpose;
- welcome message settings: title, description, embed color, image URLs, rules channel ID, and roles channel ID;
- role panel settings: panel message ID, channel ID, embed text, interaction mode, buttons, emoji, and roles.

### 2.2. User Data

The Bot may store:

- Discord user ID;
- Discord username or display name when needed for logs and embeds;
- user role IDs when needed for role assignment/removal and permission checks;
- temporary voice room owner ID;
- activity counters: message count, voice minutes, and warning count;
- join/leave dates or other server event timestamps.

### 2.3. Message Data

If logging, statistics, or AI moderation are enabled, the Bot may process:

- message ID;
- author ID;
- channel ID;
- message content;
- creation, edit, or deletion time;
- previous and updated content for edited messages when supported by enabled logging;
- deletion/edit status;
- AI review result: `ai_flagged` and `ai_reason`;
- event type: message, deletion, edit, bulk delete, and similar events.

Message content is used for moderation, audit, statistics, and server protection features. The Bot does not read private direct messages unless a user directly interacts with the Bot in DMs or Discord sends that interaction to the Bot.

### 2.4. Moderation Data

For commands such as `/warn`, `/mute`, `/kick`, `/ban`, `/history`, `/punishments list`, and similar features, the Bot may store:

- server ID;
- punished user ID;
- moderator ID;
- punishment type;
- reason;
- duration;
- expiration date;
- whether the punishment is active;
- warning, mute, kick, and ban history.

This data is needed for transparent moderation, review of previous decisions, and automatic escalation logic.

### 2.5. Voice Data

For dynamic voice rooms and statistics, the Bot may store:

- voice channel ID;
- room owner ID;
- room name;
- room creation time;
- user join and leave time for voice channels;
- voice session duration;
- room settings such as limit, access, lock status, and ownership transfer.

The Bot does not record or store audio from voice channels.

### 2.6. Statistics

The Bot may collect aggregated statistics:

- total member count;
- online member count when available through the Discord API;
- number of members in voice channels;
- message count;
- top active users and channels;
- total voice time;
- new and departed members;
- daily or periodic server activity snapshots.

### 2.7. Streams, Publications, and Dev Blog

If stream monitoring, auto-publication, or Dev Blog modules are enabled, the Bot may store:

- streamer's Discord user ID;
- platform: Twitch, YouTube, Kick, TikTok, or another supported platform;
- external channel URL or identifier;
- external channel name;
- announcement embed template;
- role ID to mention;
- last stream or publication ID to prevent duplicates;
- Dev Blog titles, text, tags, image URLs, and post IDs.

External platforms may have their own privacy policies. The Bot contacts them only for monitoring and publication features configured by server administrators or authorized users.

### 2.8. Technical Logs

The Bot writes technical logs to files to diagnose errors and maintain service stability. Logs may include:

- event time;
- module name;
- log level;
- error description;
- Discord IDs if they appear in an error message or audit event.

Logs are rotated: the current configuration uses files up to 10 MB and up to 5 backup copies.

## 3. Information We Do Not Collect

The Bot does not intentionally collect:

- Discord passwords;
- user tokens;
- payment information;
- user IP addresses;
- device or browser information;
- precise geolocation;
- biometric data;
- voice channel audio recordings;
- private direct messages unless the user interacts with the Bot directly.

## 4. How We Use Data

Data is used to:

- execute slash commands, buttons, menus, and modals;
- assign and remove roles;
- automatically assign a base role to new members;
- create and maintain role panels;
- send welcome messages and log joins/leaves;
- perform AI moderation for spam, ads, invites, NSFW content, bullying, threats, and other harmful content;
- maintain punishment history and moderator actions;
- delete messages, apply mutes, kicks, bans, slowmode, and chat cleanup;
- log deleted/edited messages and server events;
- collect server statistics;
- operate dynamic voice rooms;
- monitor streams and auto-publications;
- publish and archive Dev Blog content;
- diagnose errors, prevent abuse, and keep the service running.

## 5. AI Moderation and Ollama

AI moderation uses a self-hosted model through Ollama hosted on the Bot operator's infrastructure. This means messages used for classification are not sent to commercial external AI APIs unless the project administrator separately changes the configuration.

Messages may be sent to the local model for classification into categories such as `SPAM`, `ADVERTISEMENT`, `INVITE`, `VIOLENCE`, `BULLYING`, `NSFW`, and `SAFE`. The review result may be stored in the database as a flag and reason.

AI moderation can make mistakes. Final server actions should be supervised by administrators and moderators.

## 6. Data Sharing and Third Parties

We do not sell or rent user data.

Data may be shared with or accessible to:

- **Discord**, because the Bot operates through the Discord API and Discord infrastructure;
- **the hosting provider/VPS**, where the Bot runs and the SQLite database is stored;
- **Twitch, YouTube, Kick, TikTok/RSS services**, if stream monitoring and auto-publication are enabled;
- **Ollama on the operator's server**, if AI moderation is enabled;
- **server administrators and moderators**, if data is posted to log channels or available through moderation commands;
- **government authorities or courts**, when required by applicable law.

## 7. Data Storage and Retention

The Bot stores data in a SQLite database and technical logs on the operator's server.

Current default retention periods:

- message logs: **30 days**, unless changed with `MESSAGE_LOG_RETENTION_DAYS`;
- inactive/expired punishment history: **365 days**, unless changed with `PUNISHMENT_RETENTION_DAYS`;
- retention cleanup: approximately every **6 hours**, unless changed with `RETENTION_CLEANUP_INTERVAL_HOURS`;
- server, role, panel, welcome, channel, and voice room settings: while the Bot is used on the server or until an administrator removes/changes the setting;
- technical logs: until overwritten by log rotation or deleted by the operator.

Some data may be kept longer if needed to investigate abuse, protect the server, comply with law, or recover from a technical failure.

## 8. Access, Correction, and Deletion Requests

A user or server administrator may request:

- what data is connected to a Discord user ID or server;
- correction of an incorrect setting;
- deletion of user data;
- deletion of server data after Bot removal;
- disabling specific modules that collect more data.

To make a request, contact us using the contact method in section 1 and provide:

- Discord user ID;
- server ID if the request relates to a specific server;
- what you want us to do: export, correct, delete, or disable.

We may ask for confirmation that the requester is the relevant user or an administrator of the relevant server. Requests are usually processed within **30 days**, unless the law requires a different timeline.

## 9. Security

We use reasonable technical and organizational safeguards:

- restricted access to the VPS, database, and logs;
- storing the bot token and API keys in `.env`, not in public source code;
- technical log rotation;
- database backups when enabled by the infrastructure administrator;
- Discord permission separation: moderation commands should be available only to users with the appropriate permissions.

No system can be completely secure. If you discover a leak, vulnerability, or data access issue, report it through the contact method in section 1.

## 10. Regional Privacy Rights

Depending on your region, you may have additional rights under GDPR, UK GDPR, CCPA/CPRA, or other laws:

- the right to know what data is collected;
- the right to receive a copy of your data;
- the right to correct data;
- the right to delete data;
- the right to restrict or object to processing;
- the right to lodge a complaint with a supervisory authority.

We do not sell personal data as defined by CCPA/CPRA.

## 11. Children and Minimum Age

The Bot is not intended for users below the minimum age required by Discord and applicable law. Discord generally requires users to be at least 13 years old, but the minimum age may be higher in some countries.

If you believe the Bot stores data about a user below the required age, contact us and we will delete such data within a reasonable time.

## 12. Changes to This Policy

We may update this Privacy Policy when Bot features, infrastructure, laws, or Discord requirements change.

Material changes will be marked with a new update date. When necessary, we may also notify administrators through a support server, GitHub, changelog, or Discord message.

## 13. Contact

Privacy, deletion, and security questions: **[\[Owner Discord ID\]](https://discord.gg/wUb3Js2wzt)**..

If you are a server administrator, include the server ID and briefly describe enabled modules. If you are a user, include your Discord user ID and the server where the Bot was used.
