"""
Test script to verify RasExamples project extraction and initialization.

This script extracts multiple HEC-RAS example projects and attempts to initialize them
to check for any errors in the extraction or initialization process.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import ras_commander
sys.path.insert(0, str(Path(__file__).parent.parent))

from ras_commander import RasExamples, init_ras_project, RasPrj

# List of projects to test
PROJECTS_TO_TEST = [
    'BSTEM - Simple Example',
    'Dredging Example',
    'Reservoir Video Tutorial',
    'SIAM Example',
    'Simple Sediment Transport Example',
    'Unsteady Sediment with Concentration Rules',
    'Video Tutorial (Sediment Intro)',
    'Baxter RAS Mapper',
    'Chapter 4 Example Data',
    'ConSpan Culvert',
    'Mixed Flow Regime Channel',
    'Wailupe GeoRAS',
    'Balde Eagle Creek',
    'Bridge Hydraulics',
    'ContractionExpansionMinorLosses',
    'Culvert Hydraulics',
    'Culverts with Flap Gates',
    'Dam Breaching',
    'Elevation Controled Gates',
    'Inline Structure with Gated Spillways',
    'Internal Stage and Flow Boundary Condition',
    'JunctionHydraulics',
    'Lateral Strcuture with Gates',
    'Lateral Structure connected to a River Reach',
    'Lateral Structure Overflow Weir',
    'Lateral Structure with Culverts and Gates',
    'Lateral Structure with Culverts',
    'Levee Breaching',
    'Mixed Flow Regime',
    'Multiple Reaches with Hydraulic Structures',
    'NavigationDam',
    'Pumping Station with Rules',
    'Pumping Station',
    'Rule Operations',
    'Simplified Physical Breaching',
    'Storage Area Hydraulic Connection',
    'UngagedAreaInflows',
    'Unsteady Flow Encroachment Analysis',
    'Chippewa_2D',
    'Weise_2D',
    'BaldEagleCrkMulti2D',
    'Muncie',
    'Example 1 - Critical Creek',
    'Example 10 - Stream Junction',
    'Example 11 - Bridge Scour',
    'Example 12 - Inline Structure',
    'Example 13 - Singler Bridge (WSPRO)',
    'Example 14 - Ice Covered River',
    'Example 15 - Split Flow Junction with Lateral Weir',
    'Example 16 - Channel Modification',
    'Example 17 - Unsteady Flow Application',
    'Example 18 - Advanced Inline Structure',
    'Example 19 - Hydrologic Routing - ModPuls',
    'Example 2 - Beaver Creek',
    'Example 20 - HagerLatWeir',
    'Example 21 - Overflow Gates',
    'Example 22 - Groundwater Interflow',
    'Example 23 - Urban Modeling',
    'Example 24 - Mannings-n-Calibration',
    'Example 3 - Single Culvert',
    'Example 4 - Multiple Culverts',
    'Example 5 - Multiple Openings',
    'Example 6 - Floodway Determination',
    'Example 7 - Multiple Plans',
    'Example 8 - Looped Network',
    'Example 9 - Mixed Flow Analysis',
    'Davis',
    'Nutrient Example',
    'NewOrleansMetro',
    'BeaverLake'
]


def test_project_extraction_and_initialization():
    """Test extraction and initialization of RAS example projects."""
    
    # Save current directory
    original_dir = os.getcwd()
    
    # Change to parent directory if we're in the tests folder
    if os.path.basename(os.getcwd()) == 'tests':
        os.chdir('..')
        print(f"Changed to parent directory: {os.getcwd()}")
    
    # Results tracking
    results = {
        'successful': [],
        'extraction_failed': [],
        'initialization_failed': [],
        'errors': {}
    }
    
    total_projects = len(PROJECTS_TO_TEST)
    
    print(f"Testing {total_projects} HEC-RAS example projects...")
    print(f"Projects will be extracted to: {os.path.join(os.getcwd(), 'example_projects')}")
    
    for i, project_name in enumerate(PROJECTS_TO_TEST, 1):
        print(f"\n[{i}/{total_projects}] Testing project: {project_name}")
        print("-" * 60)
        
        try:
            # Extract the project (RasExamples handles destination automatically)
            print(f"  Extracting project...")
            extraction_path = RasExamples.extract_project(project_name)
            
            if not extraction_path:
                print(f"  [FAILED] Extraction failed: No path returned")
                results['extraction_failed'].append(project_name)
                continue
                
            print(f"  [SUCCESS] Extracted to: {extraction_path}")
            
            # Try to initialize the project
            print(f"  Initializing project...")
            try:
                # Create a custom RasPrj object for this project
                ras_project = RasPrj()
                init_ras_project(extraction_path, ras_version="6.6", ras_object=ras_project)
                
                if ras_project:
                    # Debug what attributes the object has
                    attrs = [attr for attr in dir(ras_project) if not attr.startswith('_')]
                    print(f"  Debug - RasPrj attributes: {', '.join(attrs[:10])}...")
                    
                    # Check for common attributes
                    if hasattr(ras_project, 'prj_file') and ras_project.prj_file is not None:
                        print(f"  [SUCCESS] Successfully initialized")
                        print(f"    - Project file: {ras_project.prj_file}")
                        print(f"    - Project name: {ras_project.project_name if hasattr(ras_project, 'project_name') else 'N/A'}")
                        print(f"    - Version: {ras_project.version if hasattr(ras_project, 'version') else 'N/A'}")
                        print(f"    - Plans: {len(ras_project.plan_df) if hasattr(ras_project, 'plan_df') else 0} found")
                        print(f"    - Geometries: {len(ras_project.geom_df) if hasattr(ras_project, 'geom_df') else 0} found")
                        results['successful'].append(project_name)
                    else:
                        print(f"  [FAILED] Object missing prj_file attribute or it's None")
                        results['initialization_failed'].append(project_name)
                else:
                    print(f"  [FAILED] Initialization returned None")
                    results['initialization_failed'].append(project_name)
                    
            except Exception as init_error:
                print(f"  [FAILED] Initialization error: {str(init_error)}")
                results['initialization_failed'].append(project_name)
                results['errors'][project_name] = {
                    'stage': 'initialization',
                    'error': str(init_error)
                }
                
        except Exception as extract_error:
            print(f"  [FAILED] Extraction error: {str(extract_error)}")
            results['extraction_failed'].append(project_name)
            results['errors'][project_name] = {
                'stage': 'extraction',
                'error': str(extract_error)
            }
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total projects tested: {total_projects}")
    print(f"[SUCCESS] Successful: {len(results['successful'])}")
    print(f"[FAILED] Extraction failed: {len(results['extraction_failed'])}")
    print(f"[FAILED] Initialization failed: {len(results['initialization_failed'])}")
    
    if results['extraction_failed']:
        print(f"\nExtraction Failed Projects:")
        for proj in results['extraction_failed']:
            print(f"  - {proj}")
            if proj in results['errors']:
                print(f"    Error: {results['errors'][proj]['error']}")
    
    if results['initialization_failed']:
        print(f"\nInitialization Failed Projects:")
        for proj in results['initialization_failed']:
            print(f"  - {proj}")
            if proj in results['errors']:
                print(f"    Error: {results['errors'][proj]['error']}")
    
    # Write detailed results to file
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(results_file, 'w') as f:
        f.write("RAS Examples Test Results\n")
        f.write("=" * 80 + "\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Projects: {total_projects}\n")
        f.write(f"Successful: {len(results['successful'])}\n")
        f.write(f"Extraction Failed: {len(results['extraction_failed'])}\n")
        f.write(f"Initialization Failed: {len(results['initialization_failed'])}\n")
        f.write("\n" + "=" * 80 + "\n")
        
        f.write("\nSUCCESSFUL PROJECTS:\n")
        for proj in results['successful']:
            f.write(f"  - {proj}\n")
        
        f.write("\nEXTRACTION FAILED:\n")
        for proj in results['extraction_failed']:
            f.write(f"  - {proj}\n")
            if proj in results['errors']:
                f.write(f"    Error: {results['errors'][proj]['error']}\n")
        
        f.write("\nINITIALIZATION FAILED:\n")
        for proj in results['initialization_failed']:
            f.write(f"  - {proj}\n")
            if proj in results['errors']:
                f.write(f"    Error: {results['errors'][proj]['error']}\n")
    
    print(f"\nDetailed results written to: {results_file}")
    
    # Restore original directory
    os.chdir(original_dir)
    
    return results


if __name__ == "__main__":
    print("Starting RAS Examples Initialization Test")
    print("=" * 80)
    results = test_project_extraction_and_initialization()