---
id: configuration
title: Configuration
sidebar_position: 8
---

# Configuration

Configure Synapse SDK for your environment and use cases.

## Configuration Methods

There are three ways to configure Synapse SDK:

1. **Synapse CLI**
2. **Environment variables**
3. **Configuration file**

## CLI

```bash
$ synapse config
```

## Configuration File

Create a configuration file at `~/.synapse/config.json`:

```json
{
  "backend": {
    "host": "https://api.synapse.sh",
    "token": "your-api-token"
  },
  "agent": {
    "id": "agent-uuid-123",
    "name": "My Development Agent",
    "token": "your-agent-token"
  }
}
```
