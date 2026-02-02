import requests
import sys
import os
import io
from datetime import datetime

class ChemicalEquipmentAPITester:
    def __init__(self, base_url="https://chemflow-dash-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details
        })

    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file"""
        print(f"\n🔍 Testing CSV upload with valid file...")
        
        # Create valid CSV content
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A1,Reactor,150.5,45.2,320.0
Heat Exchanger-B2,Heat Exchanger,200.3,38.5,285.0
Pump-C3,Pump,180.0,52.0,95.0"""
        
        files = {'file': ('test_equipment.csv', csv_content, 'text/csv')}
        
        try:
            response = requests.post(f"{self.base_url}/api/upload/", files=files)
            
            if response.status_code == 201:
                data = response.json()
                required_fields = ['id', 'uploaded_at', 'stats', 'data']
                
                if all(field in data for field in required_fields):
                    stats = data['stats']
                    required_stats = ['total_equipment', 'average_flowrate', 'average_pressure', 
                                    'average_temperature', 'equipment_distribution']
                    
                    if all(stat in stats for stat in required_stats):
                        if stats['total_equipment'] == 3:
                            self.log_test("Upload Valid CSV", True)
                            return True
                        else:
                            self.log_test("Upload Valid CSV", False, f"Expected 3 equipment, got {stats['total_equipment']}")
                    else:
                        self.log_test("Upload Valid CSV", False, "Missing required statistics")
                else:
                    self.log_test("Upload Valid CSV", False, "Missing required response fields")
            else:
                self.log_test("Upload Valid CSV", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Upload Valid CSV", False, str(e))
        
        return False

    def test_upload_invalid_csv(self):
        """Test uploading CSV with missing columns"""
        print(f"\n🔍 Testing CSV upload with missing columns...")
        
        # Create CSV with missing required columns
        csv_content = """Equipment Name,Type,Flowrate
Reactor-A1,Reactor,150.5
Heat Exchanger-B2,Heat Exchanger,200.3"""
        
        files = {'file': ('invalid_equipment.csv', csv_content, 'text/csv')}
        
        try:
            response = requests.post(f"{self.base_url}/api/upload/", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data and 'Missing required columns' in data['error']:
                    self.log_test("Upload Invalid CSV (Missing Columns)", True)
                    return True
                else:
                    self.log_test("Upload Invalid CSV (Missing Columns)", False, "Wrong error message")
            else:
                self.log_test("Upload Invalid CSV (Missing Columns)", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Upload Invalid CSV (Missing Columns)", False, str(e))
        
        return False

    def test_upload_non_csv_file(self):
        """Test uploading non-CSV file"""
        print(f"\n🔍 Testing upload with non-CSV file...")
        
        files = {'file': ('test.txt', 'This is not a CSV file', 'text/plain')}
        
        try:
            response = requests.post(f"{self.base_url}/api/upload/", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data and 'CSV' in data['error']:
                    self.log_test("Upload Non-CSV File", True)
                    return True
                else:
                    self.log_test("Upload Non-CSV File", False, "Wrong error message")
            else:
                self.log_test("Upload Non-CSV File", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Upload Non-CSV File", False, str(e))
        
        return False

    def test_upload_no_file(self):
        """Test upload endpoint without file"""
        print(f"\n🔍 Testing upload without file...")
        
        try:
            response = requests.post(f"{self.base_url}/api/upload/")
            
            if response.status_code == 400:
                data = response.json()
                if 'error' in data and 'No file provided' in data['error']:
                    self.log_test("Upload No File", True)
                    return True
                else:
                    self.log_test("Upload No File", False, "Wrong error message")
            else:
                self.log_test("Upload No File", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Upload No File", False, str(e))
        
        return False

    def test_get_latest_with_data(self):
        """Test getting latest upload when data exists"""
        print(f"\n🔍 Testing get latest with existing data...")
        
        try:
            response = requests.get(f"{self.base_url}/api/latest/")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'uploaded_at', 'stats', 'data']
                
                if all(field in data for field in required_fields):
                    self.log_test("Get Latest With Data", True)
                    return True
                else:
                    self.log_test("Get Latest With Data", False, "Missing required fields")
            else:
                self.log_test("Get Latest With Data", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Latest With Data", False, str(e))
        
        return False

    def test_pdf_generation(self):
        """Test PDF generation"""
        print(f"\n🔍 Testing PDF generation...")
        
        try:
            response = requests.get(f"{self.base_url}/api/pdf/")
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'application/pdf':
                    if len(response.content) > 1000:  # PDF should be substantial
                        self.log_test("PDF Generation", True)
                        return True
                    else:
                        self.log_test("PDF Generation", False, "PDF content too small")
                else:
                    self.log_test("PDF Generation", False, "Wrong content type")
            else:
                self.log_test("PDF Generation", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PDF Generation", False, str(e))
        
        return False

    def test_sample_csv_upload(self):
        """Test uploading the provided sample CSV"""
        print(f"\n🔍 Testing sample CSV upload...")
        
        try:
            # Read the sample CSV file
            with open('/app/sample_equipment_data.csv', 'r') as f:
                csv_content = f.read()
            
            files = {'file': ('sample_equipment_data.csv', csv_content, 'text/csv')}
            response = requests.post(f"{self.base_url}/api/upload/", files=files)
            
            if response.status_code == 201:
                data = response.json()
                stats = data['stats']
                
                # Should have 15 equipment items based on sample file
                if stats['total_equipment'] == 15:
                    # Check if we have proper distribution
                    distribution = stats['equipment_distribution']
                    expected_types = ['Reactor', 'Heat Exchanger', 'Pump', 'Distillation Column', 'Compressor']
                    
                    if all(eq_type in distribution for eq_type in expected_types):
                        self.log_test("Sample CSV Upload", True)
                        return True
                    else:
                        self.log_test("Sample CSV Upload", False, "Missing equipment types in distribution")
                else:
                    self.log_test("Sample CSV Upload", False, f"Expected 15 equipment, got {stats['total_equipment']}")
            else:
                self.log_test("Sample CSV Upload", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Sample CSV Upload", False, str(e))
        
        return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Chemical Equipment API Tests...")
        print(f"Testing against: {self.base_url}")
        
        # Test upload functionality
        self.test_upload_no_file()
        self.test_upload_non_csv_file()
        self.test_upload_invalid_csv()
        self.test_upload_valid_csv()
        self.test_sample_csv_upload()
        
        # Test data retrieval
        self.test_get_latest_with_data()
        
        # Test PDF generation
        self.test_pdf_generation()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = ChemicalEquipmentAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())