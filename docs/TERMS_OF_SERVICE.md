# Terms of Service for OmniBot

**Effective Date:** June 18, 2026  
**Last Updated:** June 18, 2026

These Terms of Service govern access to **OmniBot** ("the Bot", "the service", "we") and its features: roles, moderation, AI checks, logging, statistics, dynamic voice rooms, stream announcements, Dev Blog, and administrative tools.

By using the Bot, adding it to a server, or interacting with its commands, you agree to these Terms, the Bot's [Privacy Policy](./PRIVACY_POLICY.md), the [Discord Terms of Service](https://discord.com/terms), [Discord Community Guidelines](https://discord.com/guidelines), [Discord Developer Terms](https://support-dev.discord.com/hc/en-us/articles/8562894815383-Discord-Developer-Terms-of-Service), and [Discord Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy).

## 1. Service Description

OmniBot is designed to manage and automate Discord server operations:

- roles and automatic role assignment;
- interactive role panels with buttons or reactions;
- welcome messages and channel configuration;
- AI moderation through self-hosted Ollama;
- warnings, mutes, kicks, bans, slowmode, and chat cleanup;
- punishment history;
- message and server event logging in SQLite;
- server and member statistics;
- dynamic voice rooms;
- Twitch, YouTube, Kick, TikTok/RSS monitoring and auto-publications;
- Dev Blog;
- bot status, configuration, and administration commands.

The actual feature set depends on the Bot version, server settings, and Discord permissions granted to the Bot.

## 2. Who May Use the Bot

The Bot may be used by Discord users who are allowed to use Discord under their age, local laws, and Discord's rules.

Only server owners or administrators with the appropriate permissions may add the Bot to a server, configure modules, and grant permissions.

If you use the Bot on behalf of an organization, community, or server, you confirm that you have the authority to accept these Terms on their behalf.

## 3. Server Administrator Responsibilities

Server administrators are responsible for:

- granting the Bot only the Discord permissions required for selected features;
- configuring log channels so that only trusted moderators can access them;
- informing server members about enabled logging, AI moderation, and statistics collection;
- choosing AI moderation thresholds and reviewing disputed detections;
- complying with privacy laws when using the Bot to log messages and member actions;
- disabling modules that the server no longer uses;
- removing the Bot from the server if these Terms or the Privacy Policy do not fit the community.

## 4. Acceptable Use

You may use the Bot only lawfully and in good faith:

- to moderate and manage your own Discord server;
- to assign roles and configure server structure;
- to protect against spam, ads, raids, and harmful content;
- to keep transparent punishment history;
- to collect statistics and maintain the community;
- to publish streams, videos, and Dev Blog content when you have the right to publish that content.

## 5. Prohibited Use

You may not use the Bot:

- to violate Discord's Terms or applicable laws;
- to monitor members without notice and a reasonable moderation purpose;
- to collect, sell, transfer, or publish personal data without a valid basis;
- to harass, bully, discriminate against, or stalk users;
- to send mass spam, perform raids, phish, spread malicious links, or commit fraud;
- to bypass Discord permissions, limits, blocks, or technical restrictions;
- to upload, publish, or distribute illegal content;
- to grant the Bot administrator permissions without a valid need;
- to attempt to obtain the Bot token, API keys, database access, logs, or server infrastructure access;
- to perform automated actions that violate the rights of other users or servers.

We may restrict, disable, or terminate access to the Bot if its use violates these Terms, Discord rules, or creates risk for users.

## 6. AI Moderation

AI moderation is an assistive tool. It may classify messages as spam, advertising, invites, NSFW, bullying, threats, or safe content.

The AI model may make mistakes: it can miss violations or incorrectly flag normal messages. Administrators and moderators should review disputed decisions, especially when the result affects a mute, ban, or other punishment.

By using AI moderation, a server administrator agrees to:

- configure reasonable detection thresholds;
- provide clear server rules to members;
- provide a way to appeal punishments;
- avoid using AI output as the only basis for serious decisions when human review is needed.

## 7. Moderation and Punishments

The Bot may help moderators perform Discord actions: warn, mute, unmute, kick, ban, unban, purge, slowmode, and other actions.

The user who runs a command and the server administration that granted permissions are responsible for each action. The Bot does not define community rules on its own and does not replace human moderator judgment.

A user may be notified about a punishment through direct messages if the feature supports it and Discord settings allow it.

## 8. Logs and Access

The Bot may post logs to server channels and store data in SQLite. Logs may contain Discord IDs, usernames, message content, punishment reasons, and information about moderator actions.

Server administrators must restrict access to log channels. Logs may not be published outside the server or used for harassment, blackmail, doxxing, or other abuse.

## 9. User Content

User content includes messages, punishment reasons, Dev Blog posts, embed templates, image URLs, tags, comments, and other data entered through Bot commands.

You retain your rights to your content, but grant the Bot the technical right to process, store, display, and send that content through Discord as needed for enabled features.

You are responsible for ensuring that your content:

- does not violate the law;
- does not violate third-party rights;
- does not contain malware, phishing, or fraud;
- does not violate Discord rules or server rules.

## 10. External Services

Some features may contact external services:

- Discord API;
- Twitch API;
- YouTube Data API;
- Kick API or public endpoints;
- TikTok/RSS providers;
- Ollama on the operator's server;
- hosting provider/VPS.

We do not control external service policies. Use of external integrations may be governed by their own terms and privacy policies.

## 11. Availability and Service Changes

The Bot is provided "as is" and "as available". We do not guarantee:

- uninterrupted operation;
- absence of errors;
- compatibility with every server and Discord configuration;
- that commands, modules, or data formats will remain unchanged;
- that AI moderation will always be accurate.

We may update, disable, change, or remove Bot features without prior notice when needed for security, stability, Discord compliance, or project development.

## 12. Limitation of Liability

To the extent permitted by law, we are not responsible for:

- decisions made by server moderators and administrators;
- incorrect Discord permission settings;
- data loss caused by Discord, VPS, database, backup, or administrator actions;
- false positives or missed detections by AI moderation;
- message deletions, mutes, kicks, bans, or other actions performed by users through Bot commands;
- damages caused by use of, or inability to use, the Bot.

Server administrators should test critical features on a test server before enabling them on a production server.

## 13. Privacy

Data processing is described in the [Privacy Policy](./PRIVACY_POLICY.md). By continuing to use the Bot, you agree that necessary data will be processed for enabled features.

If you do not agree with data processing, stop using the Bot, disable the relevant modules, or remove the Bot from the server.

## 14. Bot Removal and Termination

An administrator may remove the Bot from a server at any time through Discord settings.

We may stop serving a server or user if:

- these Terms are violated;
- Discord rules are violated;
- usage creates a security risk;
- the Bot is used for illegal activity;
- the server attempts to gain unauthorized access to the Bot's infrastructure.

After Bot removal, some data may remain until the retention periods described in the Privacy Policy expire, unless an administrator requests earlier deletion.

## 15. Changes to These Terms

We may update these Terms when features, laws, Discord requirements, or project infrastructure change.

The new version takes effect on the date shown at the top of the document. Continued use of the Bot after an update means acceptance of the updated Terms.

## 16. Contact

Questions, complaints, data deletion requests, and vulnerability reports: **[\[Discord Support Server\]](https://discord.gg/wUb3Js2wzt)**.

When contacting us, include:

- Discord user ID;
- server ID if the issue relates to a specific server;
- a short description of the issue;
- a message or command link if it helps investigation.
