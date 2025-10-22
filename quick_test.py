#!/usr/bin/env python3
"""
Quick test for ClickUp API connectivity
Run this on Windows to verify your setup
"""

import asyncio
import httpx
import os

# Your API token
API_TOKEN = os.getenv("CLICKUP_API_TOKEN", "pk_150085995_AJH8L8QYCAH42OQXJ7OH0SUQLBU4USSZ")

async def test_clickup_api():
    """Test ClickUp API with your token"""
    print("Testing ClickUp API Connection...")
    print(f"Using token: {API_TOKEN[:20]}...")
    print()

    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Get workspaces
            print("1. Testing /team endpoint...")
            response = await client.get(
                "https://api.clickup.com/api/v2/team",
                headers=headers,
                timeout=10.0
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                teams = data.get("teams", [])
                print(f"   ✓ SUCCESS! Found {len(teams)} workspace(s)")

                if teams:
                    print("\n   Your Workspaces:")
                    for team in teams:
                        print(f"     • {team['name']}")
                        print(f"       ID: {team['id']}")
                        print()

                    # Test 2: Get spaces
                    if teams:
                        team_id = teams[0]['id']
                        print(f"2. Testing /space endpoint for workspace {team_id}...")
                        response2 = await client.get(
                            f"https://api.clickup.com/api/v2/team/{team_id}/space",
                            headers=headers,
                            params={"archived": "false"},
                            timeout=10.0
                        )

                        print(f"   Status: {response2.status_code}")
                        if response2.status_code == 200:
                            spaces_data = response2.json()
                            spaces = spaces_data.get("spaces", [])
                            print(f"   ✓ SUCCESS! Found {len(spaces)} space(s)")

                            if spaces:
                                print("\n   Your Spaces:")
                                for space in spaces[:3]:  # Show first 3
                                    print(f"     • {space['name']} (ID: {space['id']})")
                        else:
                            print(f"   ✗ Error: {response2.text}")

                print("\n" + "="*60)
                print("✓ Your ClickUp MCP server is properly configured!")
                print("✓ API token is valid and working!")
                print("="*60)
                return True

            elif response.status_code == 401:
                print("   ✗ ERROR: Invalid API token")
                print("   Please check your API token at: https://app.clickup.com/settings/apps")
                return False

            elif response.status_code == 403:
                print("   ✗ ERROR: Access denied (403)")
                print("   This usually means:")
                print("     1. The API token is invalid or expired")
                print("     2. The token doesn't have required permissions")
                print("   Please generate a new API token at:")
                print("   https://app.clickup.com/settings/apps")
                return False

            else:
                print(f"   ✗ Unexpected error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except httpx.ConnectError:
            print("   ✗ Connection error - check your internet connection")
            return False
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            return False

if __name__ == "__main__":
    print()
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "CLICKUP API QUICK TEST" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    print()

    result = asyncio.run(test_clickup_api())

    if not result:
        print("\n⚠ Test failed. Please fix the issues above before using the MCP server.")
    else:
        print("\n✓ You're ready to use the ClickUp MCP server with Claude Desktop!")
