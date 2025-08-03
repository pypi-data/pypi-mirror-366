# Slack MCP Server

A Model Context Protocol (MCP) server for Slack workspace integration using FastMCP with HTTP transport and multiuser support.

## Features

### Tools

#### **Core Messaging Tools**
- **conversations_history** - Get messages from channels/DMs with enhanced user details
- **bulk_conversations_history** - Get messages from multiple channels efficiently (avoids N API calls)
- **conversations_replies** - Get thread messages with pagination  
- **conversations_add_message** - Post messages to channels/DMs (safety disabled by default)
- **conversations_search_messages** - Search messages with advanced filters
- **message_permalink** - Get permanent links to specific messages

#### **Channel & User Management**
- **channels_list** - List all channels with sorting options
- **channels_detailed** - Get comprehensive channel info efficiently (avoids redundant API calls)
- **channel_info** - Get detailed channel information (topic, purpose, member count)
- **channel_members** - List channel members with user details
- **set_channel_topic** - Update channel topic
- **set_channel_purpose** - Update channel purpose
- **user_info** - Get detailed user information and profile (supports multiple users)
- **users_list** - List all users with filtering options (cache-only for performance)
- **user_presence** - Check user's online/away status

#### **Workspace & Analytics**
- **workspace_info** - Get workspace details (name, domain, plan)
- **analytics_summary** - Workspace analytics from cached data
- **files_list** - List files with filters by channel/user/type
- **initialize_cache** - Force creation of both cache files
- **cache_info** - Show cache file locations, sizes, and status  
- **clear_cache** - Clear cache files to force refresh
- **check_permissions** - Test what Slack API scopes are available

#### **Interactive Features**
- **add_reaction** - Add emoji reactions to messages

### Resources
- **slack://workspace/channels** - CSV directory of all channels with metadata
- **slack://workspace/users** - CSV directory of all users with metadata

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables
- `SLACK_MCP_XOXP_TOKEN` - Slack bot token (xoxb-) or user token (xoxp-)

### Optional Environment Variables
- `SLACK_MCP_ADD_MESSAGE_TOOL` - Enable message posting:
  - Not set = disabled (default for safety)
  - `true` or `1` = enabled for all channels
  - Comma-separated channel IDs = enabled only for specific channels
- `SLACK_MCP_USERS_CACHE` - Path to users cache file (default: `~/slack-cache/users_cache.json`)
- `SLACK_MCP_CHANNELS_CACHE` - Path to channels cache file (default: `~/slack-cache/channels_cache_v2.json`)

## Usage

### Start HTTP Server
```bash
python slack_mcp_server.py
```

Server runs on `http://0.0.0.0:8000/mcp` by default.

### Authentication
For multiuser support, pass the Slack token in request headers:
```
SLACK_MCP_XOXP_TOKEN: xoxb-your-slack-token
```

Optional message posting control via headers:
```
SLACK_MCP_ADD_MESSAGE_TOOL: true
```

Alternatively, set `SLACK_MCP_XOXP_TOKEN` environment variable for single-user mode.

## API Examples

### Get Channel History
```json
{
  "method": "conversations_history",
  "params": {
    "channel_id": "#general",
    "limit": "1d",
    "include_activity_messages": false
  }
}
```

### Search Messages
```json
{
  "method": "conversations_search_messages", 
  "params": {
    "search_query": "project update",
    "filter_in_channel": "#general",
    "filter_users_from": "@john",
    "limit": 50
  }
}
```

### Get Channels Directory
```json
{
  "method": "resource",
  "params": {
    "uri": "slack://myworkspace/channels"
  }
}
```

## Slack Permissions

Required scopes for your Slack app:
- **channels:history** - Read public channel messages
- **groups:history** - Read private channel messages  
- **im:history** - Read direct messages
- **mpim:history** - Read group direct messages
- **channels:read** - List public channels
- **groups:read** - List private channels
- **users:read** - List workspace users
- **chat:write** - Post messages (if enabled)

## Enhanced Features

### Intelligent Caching
- **User Cache**: Automatically caches user information to avoid repeated API calls
- **Channel Cache**: Caches channel metadata with configurable refresh intervals  
- **Performance**: Significantly reduces API rate limit usage and improves response times
- **Cache-First**: `user_info` and `channel_info` tools default to cache for instant responses
- **Fallback**: Graceful fallback to API if cache miss or explicitly requested

### Smart Name Resolution
The server now accepts user-friendly names in addition to IDs:

**Channel References:**
- `#general` → resolves to channel ID (C1234567890)
- `#project-alpha` → resolves to channel ID
- `@john_dm` → opens/finds DM with user "john"

**User References:**
- `@john` → resolves to user ID (U1234567890)
- `john.doe` → resolves using display name or real name
- `John Doe` → resolves using real name

**Examples:**
```json
// Get messages from #general channel with user details
{
  "method": "conversations_history",
  "params": {
    "channel_id": "#general",
    "limit": "1d",
    "include_user_details": true
  }
}

// Get detailed info about a user (cache-first, instant)
{
  "method": "user_info",
  "params": {
    "user_id": "@gongrzhe"
  }
}

// Get all channels efficiently (1 API call instead of N channel_info calls)
{
  "method": "channels_detailed",
  "params": {
    "channel_types": "public_channel,private_channel",
    "sort": "popularity",
    "limit": 50
  }
}

// Get messages from multiple channels efficiently (instead of N conversations_history calls)
{
  "method": "bulk_conversations_history",
  "params": {
    "channel_ids": "#general, #random, #project-alpha",
    "limit": "1d",
    "filter_user": "@chris"
  }
}

// Get fresh user info from API (slower)
{
  "method": "user_info", 
  "params": {
    "user_id": "@gongrzhe",
    "use_cache": false
  }
}

// List members of #general channel
{
  "method": "channel_members",
  "params": {
    "channel_id": "#general"
  }
}

// Get workspace analytics
{
  "method": "analytics_summary",
  "params": {
    "date_range": "30d"
  }
}

// Add reaction to a message
{
  "method": "add_reaction",
  "params": {
    "channel_id": "#general",
    "message_ts": "1699123456.123456",
    "emoji_name": "thumbsup"
  }
}

// Set channel topic
{
  "method": "set_channel_topic",
  "params": {
    "channel_id": "#general",
    "topic": "Welcome to our main discussion channel!"
  }
}

// Search messages from @john in #project-alpha
{
  "method": "conversations_search_messages", 
  "params": {
    "search_query": "deployment",
    "filter_in_channel": "#project-alpha",
    "filter_users_from": "@john"
  }
}

// List files shared by @chris
{
  "method": "files_list",
  "params": {
    "user_id": "@chris",
    "count": 20,
    "types": "images"
  }
}

// Check what permissions are available
{
  "method": "check_permissions"
}

// Initialize both cache files
{
  "method": "initialize_cache"
}

// Check cache file locations and status
{
  "method": "cache_info"
}

// Clear all cache files
{
  "method": "clear_cache",
  "params": {
    "cache_type": "both"
  }
}
```

## Security

- Message posting disabled by default for safety
- Token-based authentication for multiuser support
- No secrets logged or committed to repository
- Follows Slack API rate limits and best practices