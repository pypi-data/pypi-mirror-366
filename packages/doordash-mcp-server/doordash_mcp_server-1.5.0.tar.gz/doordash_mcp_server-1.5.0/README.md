# DoorDash MCP Server

An MCP (Model Context Protocol) server that provides DoorDash food ordering functionality to Claude Desktop.

## Important: Authentication Required

This MCP server requires a valid DoorDash organization ID to function. You must set the `DOORDASH_ORG_ID` environment variable before using this server.

To obtain an organization ID, you need to register with the DoorDash API platform.

## Features

- 🔍 Search for restaurants
- 📋 View restaurant details and menus
- 🛒 Add items to cart
- 📦 View and manage carts
- 📍 Manage delivery addresses
- 💳 View payment methods
- 🚚 Place orders (real orders with real payment!)
- 🧹 Clear carts

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/doordash-automation/doordash-mcp.git
cd doordash-mcp

# Install dependencies
pip install -r requirements.txt

# Install the MCP server
pip install -e .
```

### Option 2: Install from PyPI

```bash
pip install doordash-mcp
```

## Configuration

### 1. Set up your DoorDash Organization ID

You must obtain a valid DoorDash organization ID for API access. This is required and the server will not function without it.

Set it as an environment variable:

```bash
export DOORDASH_ORG_ID="your-org-id-here"
```

**Note**: Replace `your-org-id-here` with your actual DoorDash organization ID.

### 2. Configure Claude Desktop

Add the DoorDash MCP server to your Claude Desktop configuration.

**On macOS:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows:**
Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to the `mcpServers` section:

```json
{
  "mcpServers": {
    "doordash": {
      "command": "python",
      "args": ["-m", "doordash_mcp"],
      "env": {
        "DOORDASH_ORG_ID": "your-org-id-here"
      }
    }
  }
}
```

Or if you installed from source:

```json
{
  "mcpServers": {
    "doordash": {
      "command": "python",
      "args": ["/path/to/doordash-mcp/doordash_mcp_server.py"],
      "env": {
        "DOORDASH_ORG_ID": "your-org-id-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Usage

Once configured, you can use DoorDash tools in Claude Desktop:

### Initialize Session
```
Use the initialize_doordash tool to start a session
```

### Search for Restaurants
```
Search for "pizza" restaurants near me using the search_restaurants tool
```

### View Restaurant Menu
```
Get details for restaurant with store_id 12345 using get_restaurant_details
```

### Add Items to Cart
```
Add item 67890 from store 12345 to my cart
```

### View Cart
```
Show me my current DoorDash cart
```

### Place Order
```
Place my DoorDash order with a $5 tip
```

## Available Tools

### Session Management
- `initialize_doordash` - Initialize client and acquire session
- `release_session` - Release session when done

### Restaurant Operations
- `search_restaurants` - Search for restaurants by query or location
- `get_restaurant_details` - Get full restaurant info including menu

### Cart Operations
- `add_to_cart` - Add items to cart
- `view_cart` - View all active carts
- `clear_carts` - Clear all carts

### Order Operations
- `place_order` - Place order (charges real money!)
- `get_addresses` - Get saved delivery addresses
- `get_payment_methods` - Get saved payment methods

## Important Notes

⚠️ **WARNING**: The `place_order` tool will place REAL orders and charge your payment method! Only use it when you actually want to order food.

- Each restaurant has its own cart in DoorDash
- The most recently updated cart is used for checkout
- Sessions expire after the configured TTL (default: 60 minutes)
- Always release sessions when done to free up resources

## Development

### Running locally

```bash
# Install in development mode
pip install -e .

# Run the server
python doordash_mcp_server.py
```

### Testing with MCP

```bash
# Test the server with mcp dev tools
mcp dev doordash_mcp_server.py
```

## Troubleshooting

### Session Issues
- Make sure your organization ID is valid
- Check that you have network connectivity
- Verify the API endpoint is accessible

### Cart Issues  
- DoorDash maintains separate carts per restaurant
- Clear carts if you're having issues
- Add an item from a restaurant to make its cart active

### Order Issues
- Verify you have a valid payment method
- Check delivery address is correct
- Ensure items are still available

## License

MIT License - See LICENSE file for details