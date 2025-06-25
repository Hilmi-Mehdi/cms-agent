#!/usr/bin/env python3
"""
Simple examples of finding course PDFs using the existing OpenAI web search endpoints.
No complex tools needed - just smart queries!
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def search_course_pdfs(subject, course_level="undergraduate"):
    """Search for course PDFs using smart query patterns."""
    
    # Build smart search queries for different types of course materials
    queries = [
        f"{subject} course syllabus filetype:pdf site:edu",
        f"{subject} {course_level} lecture notes filetype:pdf university",
        f"{subject} textbook solutions filetype:pdf",
        f"{subject} problem sets homework filetype:pdf site:edu",
        f"{subject} course materials {course_level} filetype:pdf"
    ]
    
    all_results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 60)
        
        try:
            response = requests.post(f"{BASE_URL}/general-web-search", data={
                "search_query": query,
                "language": "en",
                "context": "academic"
            })
            
            if response.status_code == 200:
                result = response.json()
                search_results = result.get('data', {}).get('search_results', [])
                answer = result.get('data', {}).get('answer', '')
                
                print(f"✅ Found {len(search_results)} sources")
                
                # Show AI summary
                if answer:
                    print(f"\n🤖 AI Summary:")
                    print(answer[:200] + "..." if len(answer) > 200 else answer)
                
                # Show PDF links
                pdf_links = []
                for source in search_results:
                    url = source.get('url', '')
                    title = source.get('title', '')
                    
                    # Check if likely a PDF
                    if (url.lower().endswith('.pdf') or 
                        'pdf' in url.lower() or 
                        'filetype:pdf' in query):
                        pdf_links.append({
                            'title': title,
                            'url': url,
                            'snippet': source.get('snippet', '')
                        })
                
                print(f"📄 Potential PDFs found: {len(pdf_links)}")
                for j, pdf in enumerate(pdf_links[:3], 1):  # Show top 3
                    print(f"  {j}. {pdf['title']}")
                    print(f"     {pdf['url']}")
                
                all_results.extend(pdf_links)
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    return all_results

def quick_pdf_search(query):
    """Quick PDF search with a single optimized query."""
    print(f"\n🎯 Quick PDF Search: {query}")
    print("=" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/general-web-search", data={
            "search_query": f"{query} filetype:pdf",
            "language": "en", 
            "context": "academic"
        })
        
        if response.status_code == 200:
            result = response.json()
            search_results = result.get('data', {}).get('search_results', [])
            answer = result.get('data', {}).get('answer', '')
            
            print(f"✅ Success! Found {len(search_results)} sources")
            
            # Extract and display PDF information
            print(f"\n📚 Course Materials Found:")
            for i, source in enumerate(search_results, 1):
                print(f"  {i}. {source.get('title', 'No title')}")
                print(f"     URL: {source.get('url', '')}")
                print(f"     Preview: {source.get('snippet', '')[:100]}...")
                print()
            
            if answer:
                print(f"🧠 AI Analysis:")
                print(answer[:300] + "..." if len(answer) > 300 else answer)
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("📚 Course PDF Search Examples")
    print("Using OpenAI Web Search to Find Course Materials")
    print("=" * 70)
    
    # Example 1: Comprehensive search for machine learning materials
    print("\n🔬 Example 1: Comprehensive Machine Learning Course Search")
    ml_results = search_course_pdfs("machine learning", "undergraduate")
    
    # Example 2: Quick search for specific topics
    print("\n" + "=" * 70)
    print("🚀 Example 2: Quick Searches")
    
    quick_searches = [
        "calculus course materials university",
        "quantum mechanics lecture notes MIT",
        "linear algebra textbook solutions",
        "computer science algorithms course",
        "statistics probability theory course"
    ]
    
    for search_term in quick_searches:
        quick_pdf_search(search_term)
    
    # Example 3: Using streaming search
    print("\n" + "=" * 70)
    print("🌊 Example 3: Streaming Search")
    print("For streaming results, use:")
    print("curl -X POST 'http://localhost:8000/api/v1/search/openai-web-stream' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"query\": \"artificial intelligence course filetype:pdf site:edu\"}'")
    
    print("\n" + "=" * 70)
    print("💡 Pro Tips for Finding Course PDFs:")
    print()
    print("🎯 Search Query Strategies:")
    print("  • Add 'filetype:pdf' to focus on PDF files")
    print("  • Use 'site:edu' to search educational institutions")
    print("  • Include 'course', 'syllabus', 'lecture notes'")
    print("  • Add university names (MIT, Stanford, etc.)")
    print("  • Include course codes (CS229, MATH101, etc.)")
    print()
    print("📋 Query Templates:")
    print("  • '[SUBJECT] course syllabus filetype:pdf site:edu'")
    print("  • '[SUBJECT] lecture notes university filetype:pdf'")
    print("  • '[SUBJECT] textbook solutions filetype:pdf'")
    print("  • '[UNIVERSITY] [SUBJECT] course materials filetype:pdf'")
    print()
    print("🔄 Download PDFs:")
    print("  • Copy URLs from results")
    print("  • Use wget, curl, or browser to download")
    print("  • Example: wget 'https://example.edu/course.pdf'") 