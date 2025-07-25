# Google-Search-Console-Add-Missing-Variations
Google Search Console Add Missing Variations

When you add a site to Google Search Console it always reminds you to "add all variations" - that is http and https, and www and non-www.

But what if you have many sites already set up in the console with only one variation?  These days Google may suddenly decide it prefers an alternative, and although rel=canonical and 301 redirects are *supposed* to teach Google which one to use, it doesn't always work.

To be safe, add all 4 variations of each domain you have.

An easy task if you have 2 or 3, but what if you have hundreds?  Then this script will quickly go through all the possibilities and add in the missing ones.

You still need to do verification, but that may happen automatically, and at least this saves some typing and ensure you don't miss any.

The python script requires that you make a google api client secret and save it in a file called, client_secrets.json, in the same folder as the script.

## MCP Server with Authorization Fallback

This repository also includes `mcp_server.py` - a Model Context Protocol (MCP) server implementation with robust authorization fallback mechanisms. This server addresses the issue where some MCP clients cannot send Authorization headers correctly.

### Quick Start

```bash
# Start with authorization keys
python3 mcp_server.py --keys your-api-key

# Development mode (no auth required)
python3 mcp_server.py
```

For detailed documentation, see [MCP_SERVER_README.md](MCP_SERVER_README.md).

