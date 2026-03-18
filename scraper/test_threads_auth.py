from playwright.sync_api import sync_playwright
import urllib.parse
import time

def test_threads_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800},
            storage_state="threads_state.json"
        )
        page = context.new_page()
        
        keyword = "抓漏"
        url = f"https://www.threads.net/search?q={urllib.parse.quote(keyword)}"
        print(f"Navigating to {url} ...")
        
        # Threads relies heavily on JavaScript rendering
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        with open('threads_search.html', 'w', encoding='utf-8') as f:
            f.write(page.content())
            
        # Common containers for threads
        posts = page.locator("div[role='article']").all_inner_texts()
        print(f"Found {len(posts)} posts using role='article'.")
        
        if len(posts) == 0:
            posts = page.locator("div[data-pressable-container='true']").all_inner_texts()
            print(f"Found {len(posts)} posts using data-pressable-container.")
            
        with open('threads_result.txt', 'w', encoding='utf-8') as f:
            for i, p_text in enumerate(posts[:5]):
                f.write(f"--- Post {i+1} ---\n{p_text}\n\n")
                
        page.screenshot(path="threads_search.png")
        print("Done.")
        browser.close()

if __name__ == "__main__":
    test_threads_scrape()
