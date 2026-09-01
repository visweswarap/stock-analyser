"""
Batch scraper for multiple funds from constants.
Scrapes all URLs, waits 10 seconds between each, and saves combined results.
"""

import json
import time
from pathlib import Path
from datetime import datetime

# Import the fund lists and scraper
from funds_constants import mid_cap
from selenium_scrapper import scrape_fund


def scrape_all_funds(fund_list, list_name: str = "funds", output_dir: str = "."):
    """
    Scrape multiple funds from a list.
    
    Args:
        fund_list: List of URLs to scrape
        list_name: Name of the list (for logging/output file)
        output_dir: Directory to save results
    
    Returns:
        List of all scrape results
    """
    output_path = Path(output_dir)
    if output_dir != ".":
        output_path.mkdir(exist_ok=True)
    else:
        output_path = Path.cwd()
    
    all_results = []
    total = len(fund_list)
    
    print(f"\n{'='*70}")
    print(f"Starting batch scrape: {list_name}")
    print(f"Total funds: {total}")
    print(f"{'='*70}\n")
    
    for i, url in enumerate(fund_list, 1):
        print(f"\n[{i}/{total}] Scraping: {url}")
        print("-" * 70)
        
        try:
            result = scrape_fund(
                url=url,
                headless=True,
                save_screenshot=False,  # Skip screenshots for batch run
            )
            all_results.append(result)
            
            # Print summary
            fund_name = result["meta"].get("fund_name", "Unknown")
            holdings_count = len(result["holdings"])
            print(f"✓ Success: {fund_name} ({holdings_count} holdings)")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            all_results.append({
                "meta": {"url": url, "error": str(e)},
                "holdings": []
            })
        
        # Sleep between requests (except after last one)
        if i < total:
            sleep_time = 10
            print(f"\nWaiting {sleep_time}s before next fund...")
            time.sleep(sleep_time)
    
    # Save all results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"{list_name}_holdings_{timestamp}.json"
    
    output_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    
    print(f"\n{'='*70}")
    print(f"✓ Batch complete! Saved to: {output_file}")
    print(f"{'='*70}\n")
    
    # Print summary
    print("Summary:")
    print("-" * 70)
    successful = sum(1 for r in all_results if "error" not in r["meta"])
    total_holdings = sum(len(r["holdings"]) for r in all_results)
    
    print(f"  Successful: {successful}/{total}")
    print(f"  Failed: {total - successful}/{total}")
    print(f"  Total holdings collected: {total_holdings}")
    print()
    
    for r in all_results:
        name = r["meta"].get("fund_name", r["meta"].get("url", "?"))
        count = len(r["holdings"])
        status = "✓" if "error" not in r["meta"] else "✗"
        print(f"  {status} {name}: {count} holdings")
    
    return all_results


if __name__ == "__main__":
    # Scrape all mid-cap funds
    scrape_all_funds(mid_cap, list_name="mid_cap")
