import asyncio
import json
import sys
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
CREDENTIALS_FILE = Path(__file__).parent / "user_credentials.json"


async def test_login(username: str, password: str, description: str = ""):
    """Test login for a specific user"""
    print(f"\n🔍 Testing login for: {username} {description}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Attempt login
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                data={
                    "username": username,
                    "password": password
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print("  ✅ Login successful!")
                print(f"  🔑 Access token: {token_data['access_token'][:50]}...")
                return token_data
            else:
                print(f"  ❌ Login failed: {response.status_code}")
                print(f"  📄 Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error during login: {e}")
            return None


async def test_inventory_access(token: str, username: str):
    """Test inventory access with user token"""
    print(f"  🔍 Testing inventory access for {username}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/inventario/",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                params={"limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Inventory access successful! Found {len(data)} assets")
                if data:
                    first_asset = data[0]
                    owner = first_asset.get("DUEÑO_DE_ACTIVO", "Unknown")
                    print(f"  📦 First asset owner: {owner}")
                else:
                    print("  📦 No assets found for this user")
                return True
            else:
                print(f"  ❌ Inventory access failed: {response.status_code}")
                print(f"  📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error accessing inventory: {e}")
            return False


def load_credentials():
    """Load credentials from file"""
    if not CREDENTIALS_FILE.exists():
        return None
    
    try:
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['credentials']
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None


async def run_tests():
    """Run login and access tests for all users"""
    print("🚀 Starting user authentication and access tests...")
    
    # Load credentials
    credentials = load_credentials()
    if credentials is None:
        print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
        print("Please run create_users.py first!")
        return
    
    print(f"📊 Found {len(credentials)} users to test")
    
    successful_logins = 0
    successful_access = 0
    
    for cred in credentials:
        username = cred['username']
        password = cred['password']
        role = cred['role']
        
        # Test login
        token_data = await test_login(username, password, f"({role})")
        
        if token_data:
            successful_logins += 1
            
            # Test inventory access
            access_token = token_data['access_token']
            if await test_inventory_access(access_token, username):
                successful_access += 1
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"  👥 Total users tested: {len(credentials)}")
    print(f"  ✅ Successful logins: {successful_logins}")
    print(f"  🔓 Successful inventory access: {successful_access}")
    print(f"  ❌ Failed logins: {len(credentials) - successful_logins}")
    print(f"  🚫 Failed inventory access: {successful_logins - successful_access}")
    
    if successful_logins == len(credentials):
        print("\n🎉 All users can login successfully!")
    else:
        print(f"\n⚠ {len(credentials) - successful_logins} users failed to login")
    
    if successful_access == successful_logins:
        print("🎉 All logged-in users can access inventory!")
    else:
        print(f"⚠ {successful_logins - successful_access} users failed inventory access")


async def test_specific_user():
    """Test admin user specifically"""
    print("\n🧪 Testing Admin User")
    
    # Load credentials for reference
    credentials = load_credentials()
    if not credentials:
        print("No credentials found")
        return
    
    # Find admin user
    admin_cred = None
    for cred in credentials:
        if cred.get('is_superuser'):
            admin_cred = cred
            break
    
    if admin_cred:
        print(f"Testing admin user: {admin_cred['username']}")
        token_data = await test_login(
            admin_cred['username'], 
            admin_cred['password'],
            "(ADMIN)"
        )
        if token_data:
            await test_inventory_access(token_data['access_token'], admin_cred['username'])
    else:
        print("No admin user found in credentials")


async def check_api_status():
    """Check if API is running"""
    print("📡 Checking if API is running...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API is running!")
                return True
            else:
                print("⚠ API responded but may have issues")
                return False
        except Exception:
            print("❌ API is not running! Please start the server first:")
            print("   uvicorn main:app --reload")
            return False


if __name__ == "__main__":
    print("🔐 User Authentication Test Suite")
    print("=" * 50)
    
    async def main():
        # Check if API is running
        if not await check_api_status():
            return
        
        # Run all tests
        await run_tests()
        
        # Test admin specifically
        await test_specific_user()
    
    asyncio.run(main())