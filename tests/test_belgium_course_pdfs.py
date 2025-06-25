#!/usr/bin/env python3
"""
Test script for simplified country-specific course PDF search functionality.
This demonstrates the improved performance and simplified logic where OpenAI
handles the country-specific search intelligence.
"""

import asyncio
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_belgium_course_pdfs():
    """Test finding course PDFs specifically from Belgian institutions."""
    
    # Import the required modules
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.tools.course_pdf_finder import CoursePdfFinderTool
    
    # Initialize the tool
    tool = CoursePdfFinderTool()
    
    # Test cases for Belgian educational content
    test_cases = [
        {
            "course_topic": "macroeconomics",
            "course_level": "undergraduate",
            "institution_type": "university",
            "language": "en",
            "country_code": "be",
            "max_pdfs": 3,
            "description": "Macroeconomics from Belgian universities"
        },
        {
            "course_topic": "tax law",
            "course_level": "graduate",
            "institution_type": "university",
            "language": "en",
            "country_code": "be",
            "max_pdfs": 3,
            "description": "Belgian tax law materials"
        }
    ]
    
    print("=== Testing Simplified Belgium-Specific Course PDF Search ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_case['description']}")
        
        # Time the execution
        start_time = time.time()
        
        try:
            # Execute the tool
            result = await tool.execute(test_case)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"✅ Completed in {execution_time:.2f} seconds")
            print(f"Results for '{test_case['course_topic']}':")
            
            if result.get("pdfs"):
                for j, pdf in enumerate(result["pdfs"], 1):
                    print(f"  {j}. {pdf['title']}")
                    print(f"     URL: {pdf['url']}")
                    print(f"     Source: {pdf.get('source', 'N/A')}")
                    print()
            else:
                print("  No PDFs found")
            
            print(f"Total PDFs found: {len(result.get('pdfs', []))}")
            print("-" * 60)
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"❌ Error after {execution_time:.2f} seconds: {str(e)}")
            print("-" * 60)

async def test_performance_comparison():
    """Test performance across different countries."""
    
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.tools.course_pdf_finder import CoursePdfFinderTool
    
    tool = CoursePdfFinderTool()
    
    # Test same topic across different countries (including some unusual ones)
    countries = [
        {"code": "be", "name": "Belgium"},
        {"code": "jp", "name": "Japan"},
        {"code": "br", "name": "Brazil"},
        {"code": "za", "name": "South Africa"},
        {"code": "in", "name": "India"},
        {"code": None, "name": "International"}
    ]
    
    print("\n=== Performance Test: Any Country Code ===\n")
    print("Testing how OpenAI handles various country codes intelligently...")
    print()
    
    total_start = time.time()
    
    for country in countries:
        params = {
            "course_topic": "macroeconomics",
            "course_level": "undergraduate",
            "institution_type": "university",
            "language": "en",
            "country_code": country["code"],
            "max_pdfs": 3
        }
        
        print(f"🔍 Searching in: {country['name']} (code: {country['code'] or 'none'})")
        start_time = time.time()
        
        try:
            result = await tool.execute(params)
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"   ⏱️  Time: {execution_time:.2f}s")
            print(f"   📄 Found: {len(result.get('pdfs', []))} PDFs")
            
            if result.get("pdfs"):
                for pdf in result["pdfs"][:2]:  # Show first 2
                    domain = pdf['url'].split('/')[2]
                    print(f"   - {pdf['title']} ({domain})")
                    
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"   ❌ Error after {execution_time:.2f}s: {str(e)}")
            
        print()
    
    total_end = time.time()
    total_time = total_end - total_start
    print(f"🏁 Total execution time: {total_time:.2f} seconds")
    print(f"📊 Average per search: {total_time/len(countries):.2f} seconds")
    print("\n💡 Notice: OpenAI now handles any country code intelligently!")
    print("   No need to predefine country mappings - just pass the code!")

if __name__ == "__main__":
    print("Course PDF Finder - Simplified Belgium Test")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(test_belgium_course_pdfs())
    asyncio.run(test_performance_comparison()) 