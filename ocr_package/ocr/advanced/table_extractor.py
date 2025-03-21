import os
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class TextElement:
    """A text element with its position and confidence."""
    def __init__(self, text: str, position: Tuple[int, int], size: Tuple[int, int], confidence: float):
        self.text = text
        self.x, self.y = position
        self.width, self.height = size
        self.confidence = confidence
        # Additional properties for table detection
        self.row_index = -1
        self.col_index = -1
        
    def __repr__(self):
        return f"TextElement('{self.text}', pos=({self.x}, {self.y}), size=({self.width}, {self.height}), conf={self.confidence:.2f})"
    
    def overlaps_horizontally(self, other, tolerance=0.5):
        """Check if this element horizontally overlaps with another element."""
        self_left, self_right = self.x, self.x + self.width
        other_left, other_right = other.x, other.x + other.width
        
        overlap = min(self_right, other_right) - max(self_left, other_left)
        min_width = min(self.width, other.width)
        
        return overlap > min_width * tolerance
    
    def overlaps_vertically(self, other, tolerance=0.5):
        """Check if this element vertically overlaps with another element."""
        self_top, self_bottom = self.y, self.y + self.height
        other_top, other_bottom = other.y, other.y + other.height
        
        overlap = min(self_bottom, other_bottom) - max(self_top, other_top)
        min_height = min(self.height, other.height)
        
        return overlap > min_height * tolerance
    
    def distance_to(self, other) -> float:
        """Calculate the Euclidean distance to another element."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

class TableDetector:
    """Class to detect and extract tables from text elements with position information."""
    
    def __init__(self, row_threshold=20, col_threshold=30):
        self.row_threshold = row_threshold
        self.col_threshold = col_threshold
        
    def parse_text_positions_file(self, file_path: str) -> List[TextElement]:
        """Parse a text positions file and return a list of TextElement objects."""
        elements = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'Text: (.*), Position: \((\d+), (\d+)\), Size: (\d+)x(\d+), Confidence: (\d+)', line.strip())
                if match:
                    text = match.group(1)
                    x = int(match.group(2))
                    y = int(match.group(3))
                    width = int(match.group(4))
                    height = int(match.group(5))
                    confidence = float(match.group(6))
                    
                    elements.append(TextElement(text, (x, y), (width, height), confidence))
        
        return elements
    
    def find_tables(self, elements: List[TextElement]) -> List[List[TextElement]]:
        """Find tables in a list of text elements."""
        # Sort elements by y-position
        elements_by_y = sorted(elements, key=lambda e: e.y)
        
        # Group elements by row
        rows = []
        current_row = []
        prev_y = None
        
        for elem in elements_by_y:
            if prev_y is None or elem.y - prev_y < self.row_threshold:
                current_row.append(elem)
            else:
                if current_row:
                    rows.append(sorted(current_row, key=lambda e: e.x))
                current_row = [elem]
            prev_y = elem.y
        
        if current_row:
            rows.append(sorted(current_row, key=lambda e: e.x))
        
        # Detect tables based on row alignment
        tables = []
        current_table = []
        
        for i, row in enumerate(rows):
            if i == 0:
                current_table.append(row)
                continue
                
            prev_row = rows[i-1]
            
            # Check if current row aligns with previous row (column structure)
            alignment_score = self._calculate_alignment(prev_row, row)
            
            if alignment_score > 0.5:  # Threshold for considering rows as part of the same table
                current_table.append(row)
            else:
                if len(current_table) >= 2:  # Minimum 2 rows to consider it a table
                    tables.append(current_table)
                current_table = [row]
        
        if len(current_table) >= 2:
            tables.append(current_table)
            
        return tables
    
    def _calculate_alignment(self, row1: List[TextElement], row2: List[TextElement]) -> float:
        """Calculate alignment score between two rows."""
        if not row1 or not row2:
            return 0.0
            
        alignments = 0
        total = max(len(row1), len(row2))
        
        for elem1 in row1:
            for elem2 in row2:
                if elem1.overlaps_horizontally(elem2):
                    alignments += 1
                    break
        
        return alignments / total
    
    def extract_tables_as_dataframes(self, tables: List[List[List[TextElement]]]) -> List[pd.DataFrame]:
        """Convert detected tables to pandas DataFrames."""
        dataframes = []
        
        for table in tables:
            # Determine the number of columns based on the widest row
            num_cols = max(len(row) for row in table)
            
            # Create a 2D array to hold the table data
            data = [[''] * num_cols for _ in range(len(table))]
            
            # Fill the data array
            for r, row in enumerate(table):
                for c, elem in enumerate(row):
                    if c < num_cols:
                        data[r][c] = elem.text
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Use first row as header if it looks like a header row
            if len(df) > 1:
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
            
            dataframes.append(df)
        
        return dataframes

class PlanSpecificationsExtractor:
    """Extract sign specifications from plans document."""
    
    def __init__(self, extracted_data_dir: str):
        self.extracted_data_dir = extracted_data_dir
        self.text_files_dir = os.path.join(extracted_data_dir, 'texts')
        self.table_detector = TableDetector()
        
    def extract_atm_specifications(self) -> pd.DataFrame:
        """Extract ATM (Active Traffic Management) sign specifications."""
        # Combine relevant position data from text positions files
        elements = []
        for page_num in range(1, 5):  # Assuming relevant pages are 1-4
            position_file = os.path.join(self.text_files_dir, f'page_{page_num}_text_positions.txt')
            if os.path.exists(position_file):
                elements.extend(self.table_detector.parse_text_positions_file(position_file))
        
        # Extract tables from text elements
        tables = self.table_detector.find_tables(elements)
        dataframes = self.table_detector.extract_tables_as_dataframes(tables)
        
        # Look for ATM-related tables
        atm_specs = None
        for df in dataframes:
            # Check if dataframe appears to contain ATM specifications
            if df.shape[1] >= 3 and any('ATM' in str(col) for col in df.columns):
                atm_specs = df
                break
        
        # If we haven't found ATM specs in position files, try looking in plans_text_optimized.txt
        if atm_specs is None:
            atm_specs = self._extract_atm_specs_from_full_text()
        
        return atm_specs
    
    def _extract_atm_specs_from_full_text(self) -> Optional[pd.DataFrame]:
        """Fallback method to extract ATM specs from full text using pattern matching."""
        plans_text_file = os.path.join(self.text_files_dir, 'plans_text_optimized.txt')
        if not os.path.exists(plans_text_file):
            return None
        
        with open(plans_text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Look for sections related to ATM signs
        atm_sections = re.findall(r'(ATM\s+SITE\s+\d+[\s\S]+?(?=ATM\s+SITE\s+\d+|---\s+PAGE))', text)
        
        if not atm_sections:
            return None
        
        # Extract specifications from each section
        specs = []
        for section in atm_sections:
            site_match = re.search(r'ATM\s+SITE\s+(\d+)', section)
            if site_match:
                site_num = site_match.group(1)
                
                # Extract dimensions
                dims = re.findall(r'(\d+\'-\d+[\s\d/]*\")', section)
                dims = [dim.strip() for dim in dims if dim.strip()]
                
                # Extract sign types
                sign_types = re.findall(r'(ATM\s+TYPE\s+\d+(?:\s+SIGN)?)', section)
                sign_types = [sign_type.strip() for sign_type in sign_types if sign_type.strip()]
                
                # Create a row for this site
                if dims and sign_types:
                    specs.append({
                        'Site': f'Site {site_num}',
                        'Location': re.search(r'"L"\s+([\d+]+)', section).group(1) if re.search(r'"L"\s+([\d+]+)', section) else '',
                        'Sign Types': ', '.join(sign_types),
                        'Dimensions': ', '.join(dims[:5])  # Take first 5 dimensions
                    })
        
        if specs:
            return pd.DataFrame(specs)
        
        return None
    
    def extract_panel_schedule(self) -> pd.DataFrame:
        """Extract panel schedule information."""
        plans_text_file = os.path.join(self.text_files_dir, 'plans_text_optimized.txt')
        if not os.path.exists(plans_text_file):
            return None
        
        with open(plans_text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Look for panel schedule section
        panel_section = re.search(r'(PROJECT\s+ATCMTD\s+PANEL\s+SCHEDULE[\s\S]+?(?=PROJECT\s+ATCMTD\s+METER))', text)
        
        if not panel_section:
            return None
            
        panel_text = panel_section.group(1)
        
        # Extract rows with regular expressions
        rows = []
        for line in panel_text.split('\n'):
            match = re.search(r'(PNL-\d+)\s+L\s+STA\s+(\d+\+\d+)\s+([\d.]+)\s+([LR]T)\s+(ITS\d+)', line)
            if match:
                rows.append({
                    'Panel': match.group(1),
                    'Station': match.group(2),
                    'Offset': match.group(3),
                    'Direction': match.group(4),
                    'Sheet': match.group(5)
                })
        
        if rows:
            return pd.DataFrame(rows)
        
        return None
    
    def generate_bom(self) -> pd.DataFrame:
        """Generate a Bill of Materials based on extracted specifications."""
        # Extract ATM specifications
        atm_specs = self.extract_atm_specifications()
        
        # Extract panel schedule
        panel_schedule = self.extract_panel_schedule()
        
        # Create a BOM dataframe
        bom_items = []
        
        # Add ATM sign items if available
        if atm_specs is not None:
            for _, row in atm_specs.iterrows():
                site = row.get('Site', '')
                sign_types = row.get('Sign Types', '')
                
                if 'TYPE 1' in sign_types:
                    bom_items.append({
                        'Item': 'ATM Sign Type 1',
                        'Location': site,
                        'Quantity': sign_types.count('TYPE 1'),
                        'Description': 'Active Traffic Management Sign (Type 1)'
                    })
                
                if 'TYPE 2' in sign_types:
                    bom_items.append({
                        'Item': 'ATM Sign Type 2',
                        'Location': site,
                        'Quantity': sign_types.count('TYPE 2'),
                        'Description': 'Active Traffic Management Sign (Type 2)'
                    })
                
                if 'TYPE 3' in sign_types:
                    bom_items.append({
                        'Item': 'ATM Sign Type 3',
                        'Location': site,
                        'Quantity': sign_types.count('TYPE 3'),
                        'Description': 'Active Traffic Management Sign (Type 3)'
                    })
        
        # Add panel items if available
        if panel_schedule is not None:
            bom_items.append({
                'Item': 'Panel Board',
                'Location': 'Various',
                'Quantity': len(panel_schedule),
                'Description': 'Electrical Panel Board for ATM Signs'
            })
        
        # Look for additional items in plans text
        plans_text_file = os.path.join(self.text_files_dir, 'plans_text_optimized.txt')
        if os.path.exists(plans_text_file):
            with open(plans_text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Find mentions of equipment that should be in the BOM
            if 'ITS POLE (80 FEET)' in text:
                bom_items.append({
                    'Item': 'ITS Pole',
                    'Location': 'Various',
                    'Quantity': text.count('ITS POLE (80 FEET)'),
                    'Description': 'ITS Pole (80 Feet)'
                })
            
            if 'CCTV CAMERA (PTZ)' in text:
                bom_items.append({
                    'Item': 'CCTV Camera (PTZ)',
                    'Location': 'Various',
                    'Quantity': text.count('CCTV CAMERA (PTZ)'),
                    'Description': 'CCTV Camera with Pan/Tilt/Zoom Capability'
                })
            
            if 'CCTV CAMERA (FIXED)' in text:
                bom_items.append({
                    'Item': 'CCTV Camera (Fixed)',
                    'Location': 'Various',
                    'Quantity': text.count('CCTV CAMERA (FIXED)'),
                    'Description': 'Fixed CCTV Camera'
                })
            
            if 'RADAR DETECTOR SYSTEM' in text:
                bom_items.append({
                    'Item': 'Radar Detector System',
                    'Location': 'Various',
                    'Quantity': text.count('RADAR DETECTOR SYSTEM'),
                    'Description': 'Radar Detector System'
                })
                
            if 'COMMUNICATION CABINET' in text:
                bom_items.append({
                    'Item': 'Communication Cabinet',
                    'Location': 'Various',
                    'Quantity': text.count('COMMUNICATION CABINET'),
                    'Description': 'Communication Cabinet for ITS Equipment'
                })
                
            if 'ACTIVE TRAFFIC MANAGEMENT SIGN CONTROLLER' in text:
                bom_items.append({
                    'Item': 'ATM Sign Controller',
                    'Location': 'Various',
                    'Quantity': text.count('ACTIVE TRAFFIC MANAGEMENT SIGN CONTROLLER'),
                    'Description': 'Controller for Active Traffic Management Signs'
                })
        
        return pd.DataFrame(bom_items)

def extract_sign_specs_from_plans(extracted_data_dir: str, output_file: str = None) -> pd.DataFrame:
    """
    Extract sign specifications from plans document and optionally save to CSV.
    
    Args:
        extracted_data_dir: Directory containing extracted text data
        output_file: Optional path to save the Bill of Materials as CSV
        
    Returns:
        DataFrame containing the Bill of Materials
    """
    extractor = PlanSpecificationsExtractor(extracted_data_dir)
    bom = extractor.generate_bom()
    
    if output_file and bom is not None:
        bom.to_csv(output_file, index=False)
        print(f"Bill of Materials saved to {output_file}")
    
    return bom 