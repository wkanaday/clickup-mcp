#!/usr/bin/env python3
"""
Test script for ClickUp MCP Server
Tests basic connectivity and tool registration
"""

import os
import asyncio
import httpx

# Set API token
CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN", "pk_150085995_AJH8L8QYCAH42OQXJ7OH0SUQLBU4USSZ")
CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"

headers = {
    "Authorization": CLICKUP_API_TOKEN,
    "Content-Type": "application/json"
}


async def test_api_connectivity():
    """Test basic API connectivity and authentication"""
    print("=" * 60)
    print("TEST 1: ClickUp API Connectivity")
    print("=" * 60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CLICKUP_API_BASE_URL}/team",
                headers=headers,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                teams = data.get("teams", [])
                print(f"✓ API Connection: SUCCESS")
                print(f"✓ Authentication: VALID")
                print(f"✓ Workspaces Found: {len(teams)}")

                if teams:
                    print("\nYour Workspaces:")
                    for team in teams:
                        print(f"  • {team['name']} (ID: {team['id']})")

                return True, teams
            else:
                print(f"✗ API Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False, None

    except Exception as e:
        print(f"✗ Connection Failed: {str(e)}")
        return False, None


async def test_server_import():
    """Test if the MCP server can be imported"""
    print("\n" + "=" * 60)
    print("TEST 2: MCP Server Import")
    print("=" * 60)

    try:
        import clickup_mcp
        print("✓ Server Import: SUCCESS")

        # Check if mcp object exists
        if hasattr(clickup_mcp, 'mcp'):
            print("✓ FastMCP Instance: FOUND")

            # Try to get tools
            mcp_instance = clickup_mcp.mcp

            # Count registered tools
            tools = []
            if hasattr(mcp_instance, '_tools'):
                tools = list(mcp_instance._tools.keys())
            elif hasattr(mcp_instance, 'list_tools'):
                # Alternative way to get tools
                try:
                    tools_result = await mcp_instance.list_tools()
                    tools = [t.name for t in tools_result.tools] if hasattr(tools_result, 'tools') else []
                except:
                    pass

            if tools:
                print(f"✓ Tools Registered: {len(tools)}")
                print("\nRegistered Tools:")
                for tool_name in sorted(tools):
                    print(f"  • {tool_name}")
            else:
                print("⚠ Warning: Could not enumerate tools (this may be normal)")
                print("  Expected tools: 17")

            return True
        else:
            print("✗ FastMCP Instance: NOT FOUND")
            return False

    except ImportError as e:
        print(f"✗ Import Failed: {str(e)}")
        print("  Make sure you've installed dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_direct_tool_call():
    """Test calling a tool function directly"""
    print("\n" + "=" * 60)
    print("TEST 3: Direct Tool Execution")
    print("=" * 60)

    try:
        import clickup_mcp

        # Test list_workspaces function
        print("Testing list_workspaces() function...")
        result = await clickup_mcp.list_workspaces()

        if "Error" not in result:
            print("✓ list_workspaces: SUCCESS")
            print("\nOutput:")
            print(result)
            return True
        else:
            print(f"✗ list_workspaces: FAILED")
            print(f"  {result}")
            return False

    except Exception as e:
        print(f"✗ Tool Execution Failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "CLICKUP MCP SERVER TEST" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = []

    # Test 1: API Connectivity
    api_ok, teams = await test_api_connectivity()
    results.append(("API Connectivity", api_ok))

    # Test 2: Server Import
    import_ok = await test_server_import()
    results.append(("Server Import", import_ok))

    # Test 3: Tool Execution (only if API is working)
    if api_ok:
        tool_ok = await test_direct_tool_call()
        results.append(("Tool Execution", tool_ok))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for test_name, ok in results:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your ClickUp MCP server is working correctly!")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
