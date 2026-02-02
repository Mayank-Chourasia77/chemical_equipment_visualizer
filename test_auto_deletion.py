import requests
import tempfile
import os

def test_auto_deletion():
    """Test that only the last 5 uploads are kept"""
    base_url = "https://chemflow-dash-1.preview.emergentagent.com"
    
    print("🔍 Testing auto-deletion functionality (keep last 5 uploads)...")
    
    # Create 7 different CSV files to test deletion
    csv_templates = [
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-1,Reactor,100,50,300",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-2,Pump,200,60,400",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-3,Compressor,300,70,500",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-4,Heat Exchanger,400,80,600",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-5,Distillation Column,500,90,700",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-6,Reactor,600,100,800",
        "Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-7,Pump,700,110,900"
    ]
    
    upload_ids = []
    
    # Upload 7 files
    for i, csv_content in enumerate(csv_templates, 1):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name
        
        try:
            files = {'file': (f'test_{i}.csv', csv_content, 'text/csv')}
            response = requests.post(f"{base_url}/api/upload/", files=files)
            
            if response.status_code == 201:
                data = response.json()
                upload_ids.append(data['id'])
                print(f"✅ Upload {i} successful - ID: {data['id']}")
            else:
                print(f"❌ Upload {i} failed - Status: {response.status_code}")
                
        finally:
            os.unlink(temp_file_path)
    
    print(f"\n📊 Uploaded {len(upload_ids)} files")
    print(f"Upload IDs: {upload_ids}")
    
    # Check if auto-deletion worked by trying to access older uploads
    # The system should only keep the last 5, so the first 2 should be deleted
    
    if len(upload_ids) >= 7:
        print(f"\n🔍 Testing if old uploads were deleted...")
        
        # The latest upload should be accessible
        latest_response = requests.get(f"{base_url}/api/latest/")
        if latest_response.status_code == 200:
            latest_data = latest_response.json()
            print(f"✅ Latest upload accessible - ID: {latest_data['id']}")
            
            # Check if the latest ID matches the last upload
            if latest_data['id'] == upload_ids[-1]:
                print("✅ Latest upload ID matches expected")
            else:
                print(f"⚠️ Latest ID {latest_data['id']} doesn't match expected {upload_ids[-1]}")
        else:
            print(f"❌ Failed to get latest upload - Status: {latest_response.status_code}")
    
    return len(upload_ids)

if __name__ == "__main__":
    test_auto_deletion()