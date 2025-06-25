#!/usr/bin/env python3
"""
Example script to demonstrate the WebDocumentFinderTool.

This script now directly calls the execute() method, which handles the entire process.
"""

import asyncio
import json
import os
from pathlib import Path
import shutil # For cleaning up example download directory

# Adjust import path if your tool is in a different location or structure
# This assumes the script is run from the root of the workspace, and app is a package.
from app.tools.web_document_finder import WebDocumentFinderTool
from app.models.schemas import ToolResult # For type hinting if needed

async def run_example():
    print(" Web Document Finder Tool Usage Example ")
    print("=" * 50)

    # Initialize the tool
    finder_tool = WebDocumentFinderTool()

    # --- Scenario 1: Get links for PDFs about 'electrostatics in belgium' ---
    print("\n Scenario 1: Get links for PDFs about 'electrostatics in belgium' ")
    params_links = {
        "search_query": "fundamentals of electrostatics",
        "file_type": "pdf",
        "country_code": "be", # Belgium
        "download_files": False,
        "max_search_results": 10 # Reduced for quicker example
    }

    print(f" Calling execute() with params: {params_links}")
    result_links = await finder_tool.execute(parameters=params_links)
    
    if result_links.success:
        print("  Tool execution successful!")
        print(f"  Found files/links: {json.dumps(result_links.data.get('files'), indent=2)}")
        print(f"  Agent notes: {result_links.agent_notes}")
    else:
        print(f"  Error in tool execution: {result_links.error}")
        print(f"  Agent notes: {result_links.agent_notes}")


    # --- Scenario 2: Download DOCX files about 'quantum computing algorithms' (no country) ---
    print("\n Scenario 2: Download DOCX files for 'quantum computing algorithms' ")
    example_download_dir = Path("temp_web_downloads_example_script")
    # Clean up directory if it exists from a previous run
    if example_download_dir.exists():
        shutil.rmtree(example_download_dir)
    example_download_dir.mkdir(parents=True, exist_ok=True)
    print(f" Will attempt to download to: {example_download_dir.resolve()}")

    params_download = {
        "search_query": "review of quantum computing algorithms", # More specific query
        "file_type": "docx",
        "download_files": True,
        "download_location": str(example_download_dir.resolve()),
        "max_search_results": 5 # Small number for example
    }

    print(f" Calling execute() with params: {params_download}")
    result_download = await finder_tool.execute(parameters=params_download)

    if result_download.success:
        print("  Tool execution for downloads successful!")
        print(f"  Downloaded files report: {json.dumps(result_download.data, indent=2)}")
        print(f"  Agent notes: {result_download.agent_notes}")
        print(f"  Check the directory: {example_download_dir.resolve()}")
        if result_download.data.get('downloaded_files'):
            print(f"   Successfully downloaded: {len(result_download.data['downloaded_files'])} files")
        if result_download.data.get('download_errors'):
            print(f"   Download errors encountered: {len(result_download.data['download_errors'])} files")
            # for err in result_download.data['download_errors'][:3]: print(f"     - {err}")
    else:
        print(f"  Error in tool execution for downloads: {result_download.error}")
        print(f"  Agent notes: {result_download.agent_notes}")
    
    print("\n Example finished.")
    print(f" If you ran the download scenario, check the example download directory: {example_download_dir.resolve()}")
    print(" You might want to manually delete it if it wasn't automatically cleaned or if real files were downloaded.")
    # Example cleanup, though user should manage this for real downloaded files
    # For this script, we can offer to clean it up if it was just for testing.
    # if example_download_dir.exists() and not any(example_download_dir.iterdir()):
    #     print(f" Cleaning up empty example directory: {example_download_dir}")
    #     shutil.rmtree(example_download_dir)
    # elif example_download_dir.exists():
    #     print(f" Example directory {example_download_dir} contains files. Please review and delete manually if needed.")

if __name__ == "__main__":
    asyncio.run(run_example()) 