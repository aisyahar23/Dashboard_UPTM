#!/usr/bin/env python3
"""
Test script to verify the 7 criteria quality insights API connection
"""

import requests
import json
from pprint import pprint

def test_quality_api():
    """Test the quality insights API endpoint"""
    
    base_url = "http://localhost:5000"
    endpoint = "/dashboard/api/quality-insights"
    
    try:
        print("🧪 Testing Quality Insights API...")
        print(f"📡 Endpoint: {base_url}{endpoint}")
        
        response = requests.get(f"{base_url}{endpoint}")
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print("\n📈 Quality Meta Information:")
            pprint(data.get('meta', {}))
            
            print(f"\n🎯 Total Criteria: {len(data.get('criteria', []))}")
            
            print("\n📋 Quality Bands:")
            for band in data.get('qualityBands', []):
                print(f"  - {band.get('label', 'N/A')}: {band.get('percentage', 0)}% ({band.get('count', 0)} graduan)")
            
            print("\n🔍 Criteria Summary:")
            for i, criterion in enumerate(data.get('criteria', [])[:3]):  # Show first 3
                print(f"  {i+1}. {criterion.get('title', 'N/A')}")
                print(f"     Skor Purata: {criterion.get('average_score', 0)}/2")
                print(f"     Peratusan: {criterion.get('average_pct', 0)}%")
            
            if len(data.get('criteria', [])) > 3:
                print(f"     ... dan {len(data.get('criteria', [])) - 3} kriteria lagi")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_summary_api():
    """Test the summary API endpoint"""
    
    base_url = "http://localhost:5000"
    endpoint = "/dashboard/api/summary"
    
    try:
        print("\n🧪 Testing Summary API...")
        print(f"📡 Endpoint: {base_url}{endpoint}")
        
        response = requests.get(f"{base_url}{endpoint}")
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Summary API Response successful!")
            print(f"📈 Total Records: {data.get('total_records', 0)}")
            print(f"💼 Employment Rate: {data.get('employment_rate', 0)}%")
            print(f"🎯 Field Alignment: {data.get('field_alignment', 0)}%")
            print(f"⏱️ Avg Time to Employment: {data.get('avg_time_to_employment', 0)} bulan")
        else:
            print(f"❌ Summary API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Summary API Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting API Connection Tests...")
    print("=" * 50)
    
    test_summary_api()
    test_quality_api()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    print("\n💡 To run your Flask app:")
    print("   python app.py")
    print("\n🌐 Then visit:")
    print("   http://localhost:5000/main-dashboard")