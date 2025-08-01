# PM Studio MCP

PM Studio MCP is a Model Context Protocol (MCP) server for product management tasks. It provides a suite of tools and utilities to help product managers analyze user feedback, perform competitive analysis, generate data visualizations, and access structured data sources.

## Available Tools

| Category & Description | Tools |
|-----------------------|-------|
| 🔍 **Search & Web**<br>Google web search, website crawling | `google_web_tool`<br>`crawl_website_tool` |
| 📊 **Data & Analytics**<br>Product insights, SQL querying, charts & visualizations | `fetch_product_insights`<br>`titan_query_data_tool`<br>`titan_search_table_metadata_tool`<br>`titan_generate_sql_from_template_tool`<br>`generate_data_visualization` |
| 💼 **M365 Graph**<br>Teams messaging, email, calendar integration | `send_message_to_chat_tool`<br>`send_message_to_channel_tool`<br>`send_mail_tool`<br>`get_calendar_events` |
| 🔧 **Utilities**<br>Document conversion, greeting utility | `convert_to_markdown_tool`<br>`greeting_with_pm_studio` |


## Quick Start

### Prerequisites
- **macOS**: `brew install uv` ([Install Homebrew](https://brew.sh) first if needed)
- **Windows**: [Download uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) and ensure it's in your PATH

### MCP Server Configuration

[<img src="https://img.shields.io/badge/VS_Code-VS_Code?style=for-the-badge&label=Install%20Server&color=0098FF&labelColor=2C2C32&logoColor=white&logo=visualstudiocode" alt="Install in VS Code" width="160">](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522pm-studio-mcp-online%2522%252C%2522command%2522%253A%2522uvx%2522%252C%2522args%2522%253A%255B%2522pm-studio-mcp%2522%252C%2522--python%253Dpython3.10%2522%255D%257D)

Add the following to MCP configuration file (`setting.json` in VS Code global setting, or `mcp.json` in your project):

```js
{
  "mcpServers": {
    "pm-studio-mcp": {
      "command": "uvx",
      "args": ["pm-studio-mcp", "--python=python3.10"],
      "env": {
          "WORKING_PATH": "{YOUR_WORKSPACE_PATH}/working_dir/"
          // Add additional variables here, refer to Environment Settings below
      }
    }
  }
}
```

#### Development Mode (Local Source)
For local development, modify the configuration:
```js
{
  "command": "uv",
  "args": ["--directory", "{PATH_TO_CLONED_REPO}/src/", "run", "-m", "pm_studio_mcp"]
}
```

**Path Examples:**
- macOS: `/Users/username/Documents/pm-studio-mcp`
- Windows: `C:\\Users\\username\\Documents\\pm-studio-mcp`

### Environment Settings

Add these environment variables to the `env` section of your MCP configuration when needed.

| Variable | Required | Description |
|----------|:--------:|------------|
| `WORKING_PATH` | ✅ | A writable Directory where output files will be stored.|
| `GRAPH_CLIENT_ID` | ❌ | Microsoft Graph API authentication for Teams/Email/Calendar. |
| `REDDIT_CLIENT_ID` | ❌ | Reddit API access for Reddit data analysis tools. |
| `REDDIT_CLIENT_SECRET` | ❌ | Reddit API authentication. Must be paired with Reddit Client ID. |
| `DATA_AI_API_KEY` | ❌ | Access to Data.ai analytics for app store data and reviews. |
| `UNWRAP_ACCESS_TOKEN` | ❌ | Unwrap AI API access for sentiment analysis features. |

> **Note:** Only `WORKING_PATH` is required. Other variables can be added as needed for specific features.

## Graph Client IDs

The PM Studio MCP automatically detects the appropriate Microsoft Graph Client ID for your team based on your user identity. The detection follows this priority order:

1. **Environment variable**: Uses the `GRAPH_CLIENT_ID` environment variable if provided
2. **Auto-detection**: Uses Azure CLI and Microsoft Graph API to identify your user alias and map it to your team's Graph Client ID
3. **No Graph access**: If neither method works, Graph-related tools will be unavailable

### Team Mapping

The following teams have configured Graph Client IDs. If your alias is registered, it will be automatically detected:

| Team/Service | Supported Users |
|---------|-----------|
| Edge Consumer+ Tracy | yche, gajie, juanliu, mile, yancheng, dingxiao |
| Edge Mobile | emilywu, hongjunqiu, yingzhuang, lmike, yazhouzhou, shengjieshi, v-xiaomengli, wenyuansu, jinghuama |
| SA - Bill | tajie, xiaoxch, chenxitan, carmenwei, liyayong, yongweizhang |
| SA - Kelly + Jingwei | yugon, danliu, eviema, angliu, menghuihu, emmaxu, zhangjingwei |
| WebComFun | michachen, chfen, alexyuan, lingyanzhao, nanyin, siyangliu |

> **Note**: If your alias is not listed above, contact the maintainer to add it to the team mapping.

### Manual Configuration

To set a specific client ID (takes highest priority), add it to the environment configuration:
```js
"env": {
    "WORKING_PATH": "{YOUR_WORKSPACE_PATH}/working_dir/",
    "GRAPH_CLIENT_ID": "your-manual-client-id"
}
```

### Troubleshooting

If Graph tools are not working:
1. Check if `GRAPH_CLIENT_ID` environment variable is set correctly
2. Verify you're logged into Azure CLI (`az login`) and have Graph API access
3. Check if your user alias is in the supported users list above
4. Contact the maintainer to add your alias to the appropriate team mapping