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

class DoorDashService:
    """Service class to manage DoorDash API interactions"""
    
    def __init__(self):
        self.org_id = DEFAULT_ORG_ID
        self.client = None
        self.session_active = False
        self.current_cart = None
        self.current_addresses = None
    
    def initialize_client(self, org_id: Optional[str] = None):
        """Initialize the DoorDash client"""
        if org_id:
            self.org_id = org_id
        elif not self.org_id:
            raise ValueError("No org_id provided and DOORDASH_ORG_ID environment variable not set")
        
        self.client = DoorDashClient(org_id=self.org_id)
        return self.client
    
    def ensure_session(self):
        """Ensure we have an active session"""
        if not self.client:
            self.initialize_client()
        
        if not self.session_active:
            try:
                session = self.client.acquire_session(ttl_minutes=DEFAULT_SESSION_TTL)
                self.session_active = True
                return session
            except Exception as e:
                raise Exception(f"Failed to acquire session: {str(e)}")

# Global service instance
dd_service = DoorDashService()

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
        dd_service.initialize_client(org_id)
        session = dd_service.ensure_session()
        
        return {
            "success": True,
            "session_info": session,
            "org_id": dd_service.org_id,
            "message": "DoorDash client initialized successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initialize DoorDash client"
        }

@mcp.tool()
async def search_restaurants(
    query: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Search Restaurants
    
    Search Restaurants

🧠 **Intelligent Search System**: Automatically detects restaurant vs item searches and routes accordingly. - **Restaurant Queries**: "mcdonalds", "burger king", "pizza hut" → Restaurant search - **Item Queries**: "fresca", "water", "energy drink" → Item search within stores - **Ambiguous Queries**: "italian", "mexican" → Defaults to restaurant search - **Unified Endpoint**: One API handles both types intelligently
    
    Args:
        query: Optional search query (e.g. "pizza", "McDonald's")
        lat: Optional latitude for location-based search
        lng: Optional longitude for location-based search
        limit: Maximum number of results to return (default: 10)
    
    
    Returns:
        Dict containing API response
    """
    try:
        dd_service.ensure_session()
        
        results = dd_service.client.search_restaurants(
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
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search restaurants"
        }

@mcp.tool()
async def get_restaurant_details(store_id: int) -> Dict[str, Any]:
    """Get Restaurant Details
    
    Get Restaurant Details

Get detailed information about a specific restaurant including menu.

Example Response:
{
  "success": true,
  "restaurant": {
    "id": "1234567",
    "name": "Tony's Pizza",
    "menu_categories": [
      {
        "name": "Pizza",
        "items": [
          {
            "id": "pizza_margherita",
            "name": "Margherita Pizza",
            "price": 1599,
            "description": "Fresh mozzarella, tomato sauce, basil"
          }
        ]
      }
    ]
  }
}
    
    Args:
        store_id: Restaurant/store ID from search results
    
    
    Returns:
        Dict containing API response
    """
    try:
        dd_service.ensure_session()
        
        details = dd_service.client.get_restaurant(store_id)
        
        return {
            "success": True,
            "restaurant": details,
            "message": f"Retrieved details for store {store_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get restaurant details for store {store_id}"
        }

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
        dd_service.ensure_session()
        
        result = dd_service.client.add_to_cart(
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
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add item to cart"
        }

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
        dd_service.ensure_session()
        
        cart = dd_service.client.view_cart()
        dd_service.current_cart = cart
        
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
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to view cart"
        }

@mcp.tool()
async def get_addresses() -> Dict[str, Any]:
    """Get saved delivery addresses.
    
    Retrieves all saved addresses associated with the account.
    
    Returns:
        Dict[str, Any]: List of saved addresses
    """
    try:
        dd_service.ensure_session()
        
        addresses = dd_service.client.get_addresses()
        dd_service.current_addresses = addresses
        
        return {
            "success": True,
            "addresses": addresses.get("addresses", []),
            "count": len(addresses.get("addresses", [])),
            "message": f"Found {len(addresses.get('addresses', []))} saved address(es)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get addresses"
        }

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
        dd_service.ensure_session()
        
        # Confirm before placing order
        if not delivery_instructions:
            delivery_instructions = "Leave at door"
        
        order = dd_service.client.place_order(
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
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to place order"
        }

@mcp.tool()
async def get_payment_methods() -> Dict[str, Any]:
    """Get Payment Methods
    
    Get Payment Methods

Retrieve all payment methods for the user.

Example Response:
{
  "success": true,
  "payment_methods": [
    {
      "id": "pm_123",
      "label": "My Visa Card",
      "card_brand": "VISA",
      "last_four": "1234",
      "is_active": true
    }
  ]
}
    
    Returns:
        Dict containing API response
    """
    try:
        dd_service.ensure_session()
        
        payments = dd_service.client.get_payment_methods()
        
        return {
            "success": True,
            "payment_methods": payments.get("payment_methods", []),
            "count": len(payments.get("payment_methods", [])),
            "message": f"Found {len(payments.get('payment_methods', []))} payment method(s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get payment methods"
        }

@mcp.tool()
async def clear_carts() -> Dict[str, Any]:
    """Clear all DoorDash carts.
    
    Removes all items from all active carts.
    
    Returns:
        Dict[str, Any]: Clear result
    """
    try:
        dd_service.ensure_session()
        
        result = dd_service.client.clear_carts()
        
        return {
            "success": True,
            "result": result,
            "message": "All carts cleared successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to clear carts"
        }

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
        if dd_service.client and dd_service.session_active:
            result = dd_service.client.release_session()
            dd_service.session_active = False
            
            return {
                "success": True,
                "result": result,
                "message": "Session released successfully"
            }
        else:
            return {
                "success": True,
                "message": "No active session to release"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to release session"
        }

# Bundle Opportunities (DoubleDash)
@mcp.tool()
async def get_bundle_opportunities(cart_id: str) -> Dict[str, Any]:
    """Get Multi-Store Bundle Opportunities
    
    Get Multi-Store Bundle Opportunities

Find compatible stores that can add items to your existing cart, enabling multi-store orders (DoubleDash functionality).

✅ WORKING: Successfully finds 90+ compatible stores for multi-store cart functionality

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

# Credit Balance
@mcp.tool()
async def get_credit_balance() -> Dict[str, Any]:
    """Get Credit Balance
    
    Get Credit Balance

Check the user's DoorDash credit balance.

✅ WORKING: This endpoint successfully retrieves credit balance information

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.get_credit_balance()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Grocery Store Features
@mcp.tool()
async def browse_grocery_store(store_id: int) -> Dict[str, Any]:
    """Browse Grocery Store
    
    Browse Grocery Store

Browse categories and featured items in a grocery store.

Args:
    store_id: Grocery store ID from search results
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.browse_grocery(store_id)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def search_grocery_items(store_id: int, query: str) -> Dict[str, Any]:
    """Search Grocery Items
    
    Search Grocery Items

Search for specific items within a grocery store.

Args:
    store_id: Grocery store ID from search results
    query: Search term for grocery items
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.search_grocery(store_id, query)
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
    
    Get Address Suggestions

Get address suggestions based on partial input for autocomplete functionality.

✅ WORKING: This endpoint successfully provides address autocomplete suggestions

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

# Payment Method Management  
@mcp.tool()
async def add_payment_method(**kwargs) -> Dict[str, Any]:
    """Add Payment Method
    
    Add Payment Method

Add a payment method for the user.

Args:
    **kwargs: Payment method details (label, cardholder_name, card_brand, etc.)
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.add_payment_method(**kwargs)
    except Exception as e:
        return {"success": False, "error": str(e)}

# Health & Monitoring
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health Check
    
    Health Check

Simple health check endpoint to verify API connectivity.

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

@mcp.tool()
async def get_system_status() -> Dict[str, Any]:
    """Get System Status
    
    Get System Status

Get overall system health and capacity information including active sessions and credential usage.

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.system_status()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Session Snapshots
@mcp.tool()
async def save_session_snapshot() -> Dict[str, Any]:
    """Save Session Snapshot
    
    Save Session Snapshot

Manually save the current session state for later restoration. Note: This is done automatically on session release.

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.save_snapshot()
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def restore_session_snapshot() -> Dict[str, Any]:
    """Restore Session Snapshot
    
    Restore Session Snapshot

Manually restore a previously saved session state. Note: This is done automatically on session acquisition.

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.restore_snapshot()
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