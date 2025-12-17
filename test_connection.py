"""
Test connection to sattaking-result.in
Run: python test_connection.py
"""
import requests
import time

def test_connection():
    """Test if website is accessible"""
    url = "https://sattaking-result.in/"
    
    print("🔍 Testing connection to sattaking-result.in...")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(url, headers=headers, timeout=20)
        print(f"   ✅ Status Code: {response.status_code}")
        print(f"   ✅ Response Size: {len(response.content)} bytes")
        
        # Test 2: Check content
        print("\n2️⃣ Checking page content...")
        if 'DISAWAR' in response.text.upper() or 'GALI' in response.text.upper():
            print("   ✅ Page contains lottery data")
        else:
            print("   ⚠️  Page loaded but no lottery data found")
        
        # Test 3: Show sample content
        print("\n3️⃣ Sample content (first 500 chars):")
        print("   " + "-" * 56)
        sample = response.text[:500].replace('\n', '\n   ')
        print(f"   {sample}")
        print("   " + "-" * 56)
        
        print("\n✅ Connection test PASSED!")
        print("   Website is accessible and working.")
        
    except requests.Timeout:
        print("   ❌ TIMEOUT: Website took too long to respond")
        print("   💡 Try again or check if website is slow")
        
    except requests.ConnectionError as e:
        print("   ❌ CONNECTION ERROR: Cannot reach website")
        print(f"   💡 Details: {str(e)[:100]}")
        print("\n   Possible reasons:")
        print("   • No internet connection")
        print("   • Website is down")
        print("   • Firewall blocking access")
        print("   • DNS issue")
        
    except Exception as e:
        print(f"   ❌ ERROR: {type(e).__name__}")
        print(f"   💡 Details: {str(e)[:100]}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_connection()
