"""
JSON to CSV Converter for Legal Sections
Converts exported_sections.json to CSV format
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def json_to_csv(json_file: str, csv_file: str) -> None:
    """
    Convert JSON file to CSV format
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """
    
    # Read JSON file
    print(f"📖 Reading: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print("❌ No data found in JSON file")
        return
    
    print(f"✅ Loaded {len(data)} records")
    
    # Get all unique keys from all records
    all_keys = set()
    for record in data:
        all_keys.update(record.keys())
    
    # Sort keys for consistent column order
    fieldnames = sorted(all_keys)
    
    # Prioritize common fields first
    priority_fields = ['section_code', 'section_number', 'title', 'description', 
                      'category', 'punishment', 'source']
    
    # Reorder fieldnames to put priority fields first
    ordered_fieldnames = []
    for field in priority_fields:
        if field in fieldnames:
            ordered_fieldnames.append(field)
            fieldnames.remove(field)
    
    # Add remaining fields
    ordered_fieldnames.extend(sorted(fieldnames))
    
    # Write to CSV
    print(f"💾 Writing to: {csv_file}")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write rows
        for record in data:
            writer.writerow(record)
    
    print(f"✅ Successfully converted {len(data)} records to CSV")
    print(f"📊 Columns: {', '.join(ordered_fieldnames)}")


def batch_convert(input_dir: str = "data", output_dir: str = "data") -> None:
    """
    Convert all JSON files in a directory to CSV
    
    Args:
        input_dir: Directory containing JSON files
        output_dir: Directory to save CSV files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in {input_dir}")
        return
    
    print(f"\n🔍 Found {len(json_files)} JSON file(s)")
    print("="*70)
    
    for json_file in json_files:
        csv_file = output_path / f"{json_file.stem}.csv"
        
        print(f"\n📄 Converting: {json_file.name}")
        try:
            json_to_csv(str(json_file), str(csv_file))
        except Exception as e:
            print(f"❌ Error converting {json_file.name}: {e}")
            continue
    
    print("\n" + "="*70)
    print("🎉 Batch conversion complete!")


def main():
    """Main function with interactive menu"""
    print("="*70)
    print("📊 JSON to CSV Converter - Legal Sections")
    print("="*70)
    print()
    
    print("Select an option:")
    print("1. Convert exported_sections.json to CSV")
    print("2. Convert specific JSON file")
    print("3. Convert all JSON files in data/ folder")
    print("4. Convert scraped_data/ JSON files to CSV")
    print("0. Exit")
    print()
    
    choice = input("Enter your choice: ").strip()
    
    try:
        if choice == '1':
            json_file = "data/exported_sections.json"
            csv_file = "data/exported_sections.csv"
            
            if not Path(json_file).exists():
                print(f"❌ File not found: {json_file}")
                return
            
            json_to_csv(json_file, csv_file)
        
        elif choice == '2':
            json_file = input("Enter JSON file path: ").strip()
            csv_file = input("Enter CSV output path: ").strip()
            
            if not Path(json_file).exists():
                print(f"❌ File not found: {json_file}")
                return
            
            json_to_csv(json_file, csv_file)
        
        elif choice == '3':
            batch_convert("data", "data")
        
        elif choice == '4':
            if not Path("scraped_data").exists():
                print("❌ scraped_data/ folder not found")
                return
            
            batch_convert("scraped_data", "scraped_data")
        
        else:
            print("Exiting...")
    
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
