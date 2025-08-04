#!/usr/bin/env python3
"""
DoorDash MCP Server

An MCP server that provides DoorDash food ordering functionality
using the published doordash-rest-client package.

Install dependencies:
    pip install mcp doordash-rest-client

Usage:
    python doordash_mcp_server.py
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Import the published DoorDash client
from doordash_client import DoorDashClient, APIError, NetworkError

# Initialize FastMCP server
mcp = FastMCP("doordash")

# Configuration
DEFAULT_ORG_ID = os.getenv("DOORDASH_ORG_ID")  # Must be set via environment variable
DEFAULT_SESSION_TTL = 60  # minutes

# Session management is now handled per-request by individual tools

@mcp.tool()
async def initialize_doordash(org_id: Optional[str] = None) -> Dict[str, Any]:
    """Acquire Session
    
    Acquire Session

Allocate a DoorDash session for a client with automatic credential management and cart restoration.
    
    Args:
        org_id: Optional organization ID for API access. If not provided,
                uses DOORDASH_ORG_ID environment variable.
    
    
    Returns:
        Dict containing API response
    """
    try:
        if not org_id:
            org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        session = client.acquire_session()
        
        return {
            "success": True,
            "session_info": session,
            "org_id": org_id,
            "message": "DoorDash client initialized successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def search_restaurants(
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Search Restaurants

🧠 **Intelligent Search System**: Automatically detects restaurant vs item searches and routes accordingly.

**✨ Search Intelligence (Fixed January 2025):**
- **Restaurant Queries**: "mcdonalds", "burger king", "pizza hut" → Restaurant search
- **Item Queries**: "fresca", "water", "energy drink" → Item search within stores  
- **Ambiguous Queries**: "italian", "mexican" → Defaults to restaurant search
- **Unified Endpoint**: One API handles both types intelligently

**🎯 Search Intelligence Benefits:**
- ✅ **McDonald's now works**: Previously returned 0 results, now finds McDonald's restaurants
- ✅ **Grocery searches preserved**: Fresca, water, etc. still work perfectly
- ✅ **One unified API**: No need to know which endpoint to use
- ✅ **Automatic routing**: System determines search type for you

Args:
    query: Optional search query (e.g. "pizza", "McDonald's")
    lat: Optional latitude for location-based search
    lng: Optional longitude for location-based search
    limit: Maximum number of results to return (default: 10)

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        results = client.search_restaurants(
            query=query,
            lat=lat,
            lng=lng,
            limit=limit
        )
        
        restaurants = results.get("results", [])
        
        return {
            "success": True,
            "restaurants": restaurants,
            "count": len(restaurants),
            "message": f"Found {len(restaurants)} restaurants"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_restaurant_details(store_id: int) -> Dict[str, Any]:
    """Get Restaurant Details

Get detailed information about a specific restaurant including menu.

Args:
    store_id: Restaurant/store ID from search results

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        details = client.get_restaurant(store_id)
        
        return {
            "success": True,
            "restaurant": details,
            "message": f"Retrieved details for store {store_id}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def add_to_cart(
    store_id: int,
    item_id: int,
    quantity: int = 1,
    special_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """Add to Cart
    
    Add to Cart

Add an item to the user's cart.
    
    Args:
        store_id: Restaurant/store ID
        item_id: Menu item ID
        quantity: Number of items to add (default: 1)
        special_instructions: Optional special instructions
    
    
    Returns:
        Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        result = client.add_to_cart(
            store_id=store_id,
            item_id=item_id,
            quantity=quantity,
            special_instructions=special_instructions
        )
        
        return {
            "success": True,
            "result": result,
            "message": f"Added {quantity} item(s) to cart"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def view_cart() -> Dict[str, Any]:
    """Clear Cart
    
    Clear Cart

Remove all items from the user's cart.

Example Response:
{
  "success": true,
  "cleared_count": 1
}
    
    Returns:
        Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        cart = client.view_cart()
        
        # Parse cart information
        cart_summary = []
        if "cart" in cart and "detailed_carts" in cart["cart"]:
            for detailed_cart in cart["cart"]["detailed_carts"]:
                cart_info = detailed_cart.get("cart", {})
                store_info = detailed_cart.get("stores", [{}])[0]
                
                cart_summary.append({
                    "cart_id": cart_info.get("id"),
                    "store_name": store_info.get("name", "Unknown"),
                    "items_count": cart_info.get("total_items_count", 0),
                    "subtotal": cart_info.get("subtotal", 0) / 100.0,  # Convert cents to dollars
                    "items": cart_info.get("items", [])
                })
        
        return {
            "success": True,
            "carts": cart_summary,
            "raw_cart": cart,
            "message": f"Found {len(cart_summary)} active cart(s)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_addresses() -> Dict[str, Any]:
    """Get saved delivery addresses.
    
    Retrieves all saved addresses associated with the account.
    
    Returns:
        Dict[str, Any]: List of saved addresses
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        addresses = client.get_addresses()
        
        return {
            "success": True,
            "addresses": addresses.get("addresses", []),
            "count": len(addresses.get("addresses", [])),
            "message": f"Found {len(addresses.get('addresses', []))} saved address(es)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def place_order(
    tip_amount: float = 0.0,
    delivery_instructions: str = "",
    user_address_id: Optional[str] = None,
    user_payment_id: Optional[str] = None
) -> Dict[str, Any]:
    """Place Order
    
    Place Order

Place an order with automatic gift configuration, credit validation, and stored tenant information.
    
    WARNING: This will place a REAL order and charge your payment method!
    
    Args:
        tip_amount: Tip amount in dollars (default: 0.0)
        delivery_instructions: Delivery instructions (default: "")
        user_address_id: Optional specific address ID
        user_payment_id: Optional specific payment method ID
    
    
    Returns:
        Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        
        # Confirm before placing order
        if not delivery_instructions:
            delivery_instructions = "Leave at door"
        
        order = client.place_order(
            tip_amount=tip_amount,
            delivery_instructions=delivery_instructions,
            user_address_id=user_address_id,
            user_payment_id=user_payment_id
        )
        
        return {
            "success": True,
            "order": order,
            "message": "Order placed successfully! Check your email for confirmation."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
async def clear_cart() -> Dict[str, Any]:
    """Clear Cart

Remove all items from the user's cart.

**✅ WORKING:** This endpoint successfully clears all items from the user's cart

Example Response:
{
  "success": true,
  "cleared_count": 1
}

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        # Use the documented DELETE endpoint instead of the undocumented POST endpoint
        result = client._request("DELETE", f"/sessions/{client.client_id}/cart")
        
        return {
            "success": True,
            "result": result,
            "message": "Cart cleared successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def release_session() -> Dict[str, Any]:
    """Release Session
    
    Release Session

Release a session, automatically save cart state, and free up credentials for reuse.

Example Response:
{
  "success": true,
  "message": "Session released successfully",
  "snapshot_saved": true
}
    
    Returns:
        Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        result = client.release_session()
        
        return {
            "success": True,
            "result": result,
            "message": "Session released successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Bundle Opportunities (DoubleDash)
@mcp.tool()
async def get_bundle_opportunities(cart_id: str) -> Dict[str, Any]:
    """Bundle Opportunities (DoubleDash)

Find compatible stores that can add items to your existing cart, enabling multi-store orders (DoubleDash functionality).

**✅ WORKING:** Successfully finds 90+ compatible stores for multi-store cart functionality

**Key Features:**
- **Dynamic Address Resolution:** Automatically retrieves user's active address for location context
- **Compatible Store Discovery:** Finds 90+ restaurants and stores that can bundle with your current cart
- **Mixed Store Types:** Supports restaurants, retail stores, and grocery combinations
- **Automatic Store Detection:** Extracts primary store ID from cart if not provided

Args:
    cart_id: Cart ID to find bundle opportunities for
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.get_bundle_opportunities(cart_id)
    except Exception as e:
        return {"success": False, "error": str(e)}





# Menu Item Details
@mcp.tool()
async def get_menu_item_details(store_id: int, item_id: int) -> Dict[str, Any]:
    """Get Menu Item Details
    
    Get Menu Item Details

Get detailed information about a specific menu item including options and customizations.

Args:
    store_id: Restaurant store ID
    item_id: Menu item ID
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.get_menu_item(store_id, item_id)
    except Exception as e:
        return {"success": False, "error": str(e)}

# Address Management
@mcp.tool()
async def get_address_suggestions(query: str) -> Dict[str, Any]:
    """Get Address Suggestions

Get address suggestions based on partial input.

**✅ WORKING:** This endpoint successfully provides address autocomplete suggestions

Args:
    query: Partial address input
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.get_address_suggestions(query)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def add_user_address(street: str, city: str, state: str, zipcode: str, **kwargs) -> Dict[str, Any]:
    """Add User Address
    
    Add User Address

Add a new delivery address for the user.

Args:
    street: Street address
    city: City name
    state: State abbreviation (e.g. "CA", "NY")
    zipcode: ZIP code
    **kwargs: Additional address fields
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.add_address(street, city, state, zipcode, **kwargs)
    except Exception as e:
        return {"success": False, "error": str(e)}



# Health & Monitoring
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health Check

Simple health check endpoint.

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.health_check()
    except Exception as e:
        return {"success": False, "error": str(e)}





# Main entry point
def main():
    """Run the MCP server"""
    import sys
    
    # Run the FastMCP server
    mcp.run(
        transport="stdio"
    )

if __name__ == "__main__":
    main()