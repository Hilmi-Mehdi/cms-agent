#!/usr/bin/env python3
"""
API Usage Examples for Science Made Simple Document Analysis

This file demonstrates how to use the new /api/v1/analyze-document endpoint
to analyze documents from the Science Made Simple API.
"""

import httpx
import asyncio
import json
import os
import shutil


async def analyze_document_basic():
    """Basic document analysis example."""
    
    print("📄 Basic Document Analysis")
    print("=" * 40)
    
    url = "http://localhost:8001/api/v1/analyze-document"
    
    # Basic parameters
    data = {
        "document_id": "ct13hjqcchrs715kgjl0",  # Your document ID
        "ai_provider": "openai",
        "analysis_depth": "basic",
        "target_audience": "general"
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                analysis = result["analysis_result"]
                doc_name = analysis["document_metadata"]["Name"]
                images_count = analysis.get("images_analyzed", 0)
                
                print(f"✅ Analysis complete for: {doc_name}")
                print(f"🖼️  Images analyzed: {images_count}")
                return result
            else:
                print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    return None


async def analyze_document_comprehensive():
    """Comprehensive document analysis with all features."""
    
    print("\n🔍 Comprehensive Document Analysis")
    print("=" * 40)
    
    url = "http://localhost:8001/api/v1/analyze-document"
    
    # Comprehensive parameters
    data = {
        "document_id": "ct13hjqcchrs715kgjl0",
        "ai_provider": "openai",
        "analysis_depth": "comprehensive",
        "target_audience": "intermediate",
        "subject_area": "physics"  # Optional: specify subject area
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                analysis = result["analysis_result"]
                
                # Document info
                doc_meta = analysis["document_metadata"]
                print(f"📄 Document: {doc_meta['Name']}")
                print(f"📋 Pages: {doc_meta.get('PageCount', 'N/A')}")
                
                # Analysis results
                if "analysis_summary" in analysis:
                    summary = analysis["analysis_summary"]
                    print(f"📚 Course Title: {summary.get('course_title', 'N/A')}")
                    print(f"🎯 Subject: {summary.get('subject_area', 'N/A')}")
                    print(f"📊 Difficulty: {summary.get('difficulty_level', 'N/A')}")
                    print(f"🖼️  Images: {summary.get('images_analyzed', 0)}")
                
                # Generated content
                if "generated_summary" in analysis:
                    summary_content = analysis["generated_summary"]
                    print(f"📝 Generated Summary: {len(summary_content.get('generated_content', {}).get('content', ''))} characters")
                
                print(f"⏱️  Execution Time: {result.get('execution_time', 'N/A')} seconds")
                print(f"🔧 Next Tools: {', '.join(result.get('suggested_next_tools', []))}")
                
                return result
            else:
                print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    return None


async def batch_analyze_documents():
    """Example of analyzing multiple documents."""
    
    print("\n📦 Batch Document Analysis")
    print("=" * 40)
    
    # List of document IDs to analyze
    document_ids = [
        "ct13hjqcchrs715kgjl0",
        # Add more document IDs as needed
    ]
    
    results = []
    
    for doc_id in document_ids:
        print(f"\n📄 Processing document: {doc_id}")
        
        url = "http://localhost:8001/api/v1/analyze-document"
        data = {
            "document_id": doc_id,
            "ai_provider": "openai",
            "analysis_depth": "detailed",
            "target_audience": "intermediate"
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(url, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        analysis = result["analysis_result"]
                        doc_name = analysis["document_metadata"]["Name"]
                        images = analysis.get("images_analyzed", 0)
                        
                        print(f"  ✅ {doc_name} - {images} images")
                        results.append({
                            "document_id": doc_id,
                            "name": doc_name,
                            "images_analyzed": images,
                            "analysis": analysis
                        })
                    else:
                        print(f"  ❌ Failed: {result['error']}")
                else:
                    print(f"  ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print(f"\n📊 Batch Results: {len(results)} documents processed successfully")
    return results


def save_analysis_results(analysis_result, filename="analysis_result.json"):
    """Save analysis results to a JSON file."""
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")


async def analyze_and_save():
    """Analyze a document and save results to file."""
    
    print("\n💾 Analyze and Save Example")
    print("=" * 40)
    
    # Perform analysis
    result = await analyze_document_comprehensive()
    
    if result and result["success"]:
        # Save results
        doc_id = result["analysis_result"]["document_id"]
        filename = f"analysis_{doc_id}.json"
        save_analysis_results(result, filename)
        
        # Also save just the summary for quick reference
        if "analysis_summary" in result["analysis_result"]:
            summary = result["analysis_result"]["analysis_summary"]
            summary_filename = f"summary_{doc_id}.json"
            save_analysis_results(summary, summary_filename)
            print(f"📋 Summary saved to: {summary_filename}")
    else:
        print("❌ No results to save")


async def find_web_documents_example():
    """Example of using the /api/v1/find-web-documents endpoint."""
    print("\n🔍 Find Web Documents API Example")
    print("=" * 40)
    
    base_url = "http://localhost:8001/api/v1/find-web-documents"

    # Scenario 1: Get PDF links
    print("\n Scenario 1: Get PDF links for 'renewable energy policies europe'")
    params_links = {
        "search_query": "renewable energy policies europe",
        "file_type": "pdf",
        "country_code": None, # Search broadly first
        "download_files": "false", # Note: form data often comes as strings
        "max_search_results": "10"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response_links = await client.post(base_url, data=params_links)
            response_links.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            result_links = response_links.json()
            
            if result_links.get("success"):
                print("  ✅ Link search successful!")
                found_files = result_links.get("response", {}).get("files", [])
                print(f"  Found {len(found_files)} PDF links:")
                for i, link in enumerate(found_files[:3]): # Print first 3 links
                    print(f"    {i+1}. {link}")
                if len(found_files) > 3: print("    ...")
            else:
                print(f"  ❌ Link search failed: {result_links.get('error_message', 'Unknown error')}")
                if result_links.get("execution_details"): print(f"     Details: {result_links.get("execution_details").get('agent_notes')}")

        except httpx.HTTPStatusError as e:
            print(f"  ❌ HTTP Error (Links): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"  ❌ Request Error (Links): {e}")
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON Decode Error (Links): {e}")

    # Scenario 2: Download DOCX files
    print("\n Scenario 2: Download DOCX files for 'ai research papers 2023'")
    download_dir = "temp_api_downloads"
    # Ensure clean slate for example downloads
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir, exist_ok=True)
    print(f"  Attempting to download to: {os.path.abspath(download_dir)}")

    params_download = {
        "search_query": "latest ai research papers 2023",
        "file_type": "docx",
        "download_files": "true",
        "download_location": os.path.abspath(download_dir),
        "max_search_results": "5" # Limit for example speed
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response_download = await client.post(base_url, data=params_download)
            response_download.raise_for_status()
            result_download = response_download.json()

            if result_download.get("success"):
                print("  ✅ Download request processed successfully!")
                data = result_download.get("response", {})
                downloaded = data.get("downloaded_files", [])
                errors = data.get("download_errors", [])
                print(f"  Files found: {data.get('files_found_count', 0)}")
                print(f"  Successfully downloaded: {len(downloaded)} files")
                for i, filepath in enumerate(downloaded[:3]): # Print first 3
                    print(f"    {i+1}. {filepath}")
                if len(downloaded) > 3: print("    ...")
                
                if errors:
                    print(f"  Download errors encountered: {len(errors)}")
                    for i, err in enumerate(errors[:2]): # Print first 2 errors
                        print(f"    - {err}")
                    if len(errors) > 2: print("    ...")
            else:
                print(f"  ❌ Download request failed: {result_download.get('error_message', 'Unknown error')}")
                if result_download.get("execution_details"): print(f"     Details: {result_download.get("execution_details").get('agent_notes')}")
        
        except httpx.HTTPStatusError as e:
            print(f"  ❌ HTTP Error (Downloads): {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"  ❌ Request Error (Downloads): {e}")
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON Decode Error (Downloads): {e}")
    
    print("\n Find Web Documents API Example Finished.")
    print(f" If downloads were attempted, check: {os.path.abspath(download_dir)}")
    print(f" Consider deleting this directory when done: shutil.rmtree('{os.path.abspath(download_dir)}')")


async def general_web_search_api_example():
    """Example of using the /api/v1/general-web-search endpoint."""
    print("\n🌐 General Web Search API Example")
    print("=" * 40)
    
    base_url = "http://localhost:8001/api/v1/general-web-search"

    search_terms = [
        "exam dates for University of Brussels Fall 2024",
        "what subjects does Ghent University teach in Computer Science?"
    ]

    for term in search_terms:
        print(f"\n Searching for: '{term}'")
        params = {
            "search_query": term,
            "max_results": "5", # Form data is string
            "region": "be-fr" # Example: Belgium, French
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(base_url, data=params)
                response.raise_for_status()
                result = response.json()
                
                if result.get("success"):
                    print(f"  ✅ Search successful: {result.get('response')}")
                    search_hits = result.get("data", {}).get("search_results", [])
                    print(f"  Found {len(search_hits)} search results:")
                    for i, hit in enumerate(search_hits[:3]): # Print top 3
                        print(f"    {i+1}. {hit.get('title')}")
                        print(f"       Link: {hit.get('url')}")
                        snippet = hit.get('snippet', '')
                        print(f"       Snippet: {snippet[:100]}..." if snippet else "")
                else:
                    print(f"  ❌ Search failed: {result.get('error_message', 'Unknown error')}")
                    if result.get("execution_details"): print(f"     Details: {result.get("execution_details").get('agent_notes')}")

            except httpx.HTTPStatusError as e:
                print(f"  ❌ HTTP Error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                print(f"  ❌ Request Error: {e}")
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON Decode Error: {e}")
        print("-" * 30)
    print("\n General Web Search API Example Finished.")


if __name__ == "__main__":
    async def main():
        print("🚀 Science Made Simple API - Document Analysis Examples")
        print("=" * 70)
        
        # Run examples
        await analyze_document_basic()
        await analyze_document_comprehensive()
        await batch_analyze_documents()
        await analyze_and_save()
        await find_web_documents_example()
        await general_web_search_api_example()
        
        print("\n" + "=" * 70)
        print("🎉 All examples completed!")
        print("\n💡 Usage Tips:")
        print("   • Use 'basic' analysis for quick overviews")
        print("   • Use 'comprehensive' for full analysis with summaries")
        print("   • Set appropriate target_audience for better results")
        print("   • Save results for later processing or comparison")
        print("\n🔧 API Endpoint: POST /api/v1/analyze-document")
        print("📋 Required: document_id")
        print("⚙️  Optional: ai_provider, analysis_depth, target_audience, subject_area")
        print("\n🔧 API Endpoint: POST /api/v1/find-web-documents")
        print("📋 Required: search_query")
        print("⚙️  Optional: file_type, country_code, download_files, download_location, max_search_results")
        print("\n🔧 API Endpoint: POST /api/v1/general-web-search")
        print("📋 Required: search_query")
        print("⚙️  Optional: max_results, region")
    
    asyncio.run(main())    