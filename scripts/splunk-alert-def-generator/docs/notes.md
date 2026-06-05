docker run -p 8000:8000 -p 8089:8089 -e "SPLUNK_PASSWORD=clus26demo" --name splunk splunk-docker

docker start splunk
docker stop splunk

docker exec -it splunk bash

## Splunk MCP server
- https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/configure-the-splunk-mcp-server
- Must enable token auth for splunk MCP servers - https://help.splunk.com/en/splunk-cloud-platform/administer/manage-users-and-security/10.3.2512/authenticate-into-the-splunk-platform-with-tokens/enable-or-disable-token-authentication
- Splunk AI Assistant: https://help.splunk.com/en/splunk-cloud-platform/search/splunk-ai-assistant/2.0.0/install-and-configure-splunk-ai-assistant/install-splunk-ai-assistant-for-splunk-cloud-customers 

### mcp.json configuration

```jsonc
"splunk-mcp-server": {
    "command": "npx",
    "args": [
        "-y",
        "mcp-remote",
        "https://127.0.0.1:8089/services/mcp",
        "--header",
        "Authorization: Bearer ${input:splunk_token}"
    ],
    "type": "stdio",
    "env": {
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
    }

}
```

Input variable (add to `inputs` array):
```jsonc
{
    "id": "splunk_token",
    "type": "promptString",
    "description": "Splunk API Token",
    "password": true
}
```

- Connects via `mcp-remote` proxy to the Splunk MCP endpoint at `https://127.0.0.1:8089/services/mcp`
- Authenticates with a Splunk API token (Bearer auth) — prompted at connect time
- Token auth must be enabled in Splunk before use (see link above)

