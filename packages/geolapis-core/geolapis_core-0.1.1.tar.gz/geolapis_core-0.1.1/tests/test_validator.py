# tests/test_validator.py
import lasio
import os
import unittest
from pathlib import Path
from tools.error_injector import corrupt_las, ErrorType
from products.las_validator_pro.cli import validate_las

class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path("test_data")
        cls.clean_las = cls.test_dir / "clean.las"
        
        # Create test directory if needed
        cls.test_dir.mkdir(exist_ok=True)
        
        # Create a properly structured clean LAS file
        if not cls.clean_las.exists():
            # Create the LAS file content directly with proper formatting
            las_content = """~VERSION INFORMATION
VERS. 2.0: CWLS log ASCII Standard
WRAP. NO: One line per depth step
DLM. SPACE: Column delimiter

~WELL INFORMATION
#MNEM.UNIT  VALUE           DESCRIPTION
#---------  -------------   --------------------------
NULL.       -999.25         : Null value
COMP.       TEST            : Company
WELL.       EXAMPLE         : Well name
STRT.M      1000.0          : Start depth
STOP.M      1002.0          : Stop depth
STEP.M      0.5             : Step

~CURVE INFORMATION
#MNEM.UNIT  API CODE        DESCRIPTION
#---------  -------------   --------------------------
DEPT.M                      : Depth
GR  .GAPI                   : Gamma Ray
RHOB.G/CC                   : Bulk Density

~PARAMETER INFORMATION
#MNEM.UNIT  VALUE           DESCRIPTION
#---------  -------------   --------------------------

~OTHER INFORMATION
#Any other information goes here

~ASCII
1000.0 50.0 2.40
1000.5 60.0 2.50
1001.0 55.0 2.45
1001.5 70.0 2.60
1002.0 65.0 2.55
"""
            # Write directly to file with proper encoding and line endings
            with open(cls.clean_las, 'w', encoding='ascii', newline='\n') as f:
                f.write(las_content)
    
    def setUp(self):
        # Create unique temp file for each test
        self.dirty_las = self.test_dir / f"dirty_{self._testMethodName}.las"
        if self.dirty_las.exists():
            self._safe_unlink(self.dirty_las)
    
    def tearDown(self):
        # Clean up after each test
        if self.dirty_las.exists():
            self._safe_unlink(self.dirty_las)
    
    def _safe_unlink(self, path):
        """Safely delete a file with retries"""
        try:
            path.unlink()
        except PermissionError:
            import time
            time.sleep(0.1)
            path.unlink(missing_ok=True)
    
    def test_detects_missing_version(self):
        """Test that version section errors are caught"""
        # Read and modify the file directly
        with open(self.clean_las, 'r', encoding='ascii') as f:
            content = f.read()
        
        # Remove VERS line while maintaining section structure
        modified_content = []
        in_version = False
        for line in content.splitlines():
            if line.startswith('~VERSION'):
                in_version = True
                modified_content.append(line)
            elif in_version and line.startswith('VERS.'):
                continue  # Skip the VERS line
            else:
                modified_content.append(line)
                if in_version and not line.strip():
                    in_version = False
        
        # Write modified version with proper line endings
        with open(self.dirty_las, 'w', encoding='ascii', newline='\n') as f:
            f.write('\n'.join(modified_content))
        
        errors = validate_las(str(self.dirty_las))
        self.assertTrue(any("VERS" in e for e in errors))
    
    def test_detects_gr_anomaly(self):
        """Test that GR curve anomalies are detected"""
        # Read and modify GR values
        with open(self.clean_las, 'r', encoding='ascii') as f:
            lines = f.readlines()
        
        # Find and modify ASCII data section
        ascii_start = next(i for i, line in enumerate(lines) if line.startswith('~ASCII'))
        for i in range(ascii_start + 1, len(lines)):
            if lines[i].strip():
                parts = lines[i].split()
                if len(parts) >= 2:  # Ensure we have GR values
                    parts[1] = str(float(parts[1]) * 2)  # Double GR values
                    lines[i] = ' '.join(parts) + '\n'
        
        # Write with proper line endings
        with open(self.dirty_las, 'w', encoding='ascii', newline='\n') as f:
            f.writelines(lines)
        
        errors = validate_las(str(self.dirty_las))
        self.assertTrue(any("GR" in e for e in errors))
    
    def test_detects_null_value_issues(self):
        """Test NULL value standardization"""
        # Read and modify NULL value
        with open(self.clean_las, 'r', encoding='ascii') as f:
            lines = f.readlines()
        
        # Find and modify NULL line
        for i, line in enumerate(lines):
            if line.startswith('NULL.'):
                parts = line.split()
                if len(parts) >= 2:
                    lines[i] = line.replace(parts[1], '999')
                break
        
        # Write with proper line endings
        with open(self.dirty_las, 'w', encoding='ascii', newline='\n') as f:
            f.writelines(lines)
        
        errors = validate_las(str(self.dirty_las))
        self.assertTrue(any("NULL" in e for e in errors))
    
    def test_detects_unit_mismatches(self):
        """Test unit consistency checks"""
        # Read and modify GR units
        with open(self.clean_las, 'r', encoding='ascii') as f:
            lines = f.readlines()
        
        # Find and modify GR unit
        for i, line in enumerate(lines):
            if 'GR  .GAPI' in line:
                lines[i] = line.replace('GAPI', 'API')
                break
        
        # Write with proper line endings
        with open(self.dirty_las, 'w', encoding='ascii', newline='\n') as f:
            f.writelines(lines)
        
        errors = validate_las(str(self.dirty_las))
        self.assertTrue(any("unit" in e.lower() for e in errors))
    
    def test_detects_mnemonic_variations(self):
        """Test mnemonic standardization"""
        # Read and modify GR mnemonic
        with open(self.clean_las, 'r', encoding='ascii') as f:
            lines = f.readlines()
        
        # Find and modify GR mnemonic
        for i, line in enumerate(lines):
            if 'GR  .GAPI' in line:
                lines[i] = line.replace('GR  .', 'GAMMA.')
                break
        
        # Write with proper line endings
        with open(self.dirty_las, 'w', encoding='ascii', newline='\n') as f:
            f.writelines(lines)
        
        errors = validate_las(str(self.dirty_las))
        self.assertTrue(any("mnemonic" in e.lower() for e in errors))

if __name__ == "__main__":
    unittest.main(failfast=True)