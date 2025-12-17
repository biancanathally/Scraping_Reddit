import requests
import json
import csv
import time
from bs4 import BeautifulSoup
from pathlib import Path

# Function -> Main Scraper to get content from Reddit
def scrape_reddit() -> list[dict]:
    subreddits = [
        "https://www.reddit.com/r/Python",
        "https://www.reddit.com/r/learnpython"
    ]

    all_data = []
    for url in subreddits:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        subreddit_name = url.split("/")[-1]  # -2?
        print(f"Scraping subreddit: {subreddit_name}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            subreddit_data = {
                "subreddit" : subreddit_name,
                "url" : url,
                "title" : soup.title.string if soup.title else "No title",
                "scraped_at" : time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            topics = []

            for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
                text = heading.get_text(strip=True)

                if text and len(text) > 3:
                    if any(
                        keyword in text.lower()
                        for keyword in [
                            "python",
                            "programming",
                            "code",
                            "develop",
                            "coding",
                        ]
                    ):
                        topics.append({"title": text, "type": "python_topic"})

            discussions = []
            seen_urls = set()

            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]

                if (
                    text
                    and len(text) > 1
                    and "/comments/" in href
                    and href not in seen_urls
                ):
                    seen_urls.add(href)

                    discussions.append(
                        {
                            "title": text[:100] + "..." if len(text) > 100 else text,
                            "url": href,
                            "type": "discussion",
                        }
                    )

            subreddit_data["python_topics"] = topics
            subreddit_data["discussions"] = discussions

            all_data.append(subreddit_data)
            time.sleep(2)

        except Exception as e:
            print(f"ERROR: {e}")

    return all_data

# Function -> Save scraped data (Both JSON and CSV formats)
def save_scraped_data(data, filename_json="python_topics.json", filename_csv="python_topics.csv"):
    if not data:
        print(f"No data to save.")
        return

    current_dir = Path(__file__).parent.absolute()
    
    path_json = current_dir / filename_json
    path_csv = current_dir / filename_csv
    
    # JSON
    try:
        with open(filename_json, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=True)
        print(f"Python topics saved: {filename_json}")
    except Exception as e:
        print(f"ERROR: {e}")
        
    # CSV
    try:
        with open(filename_csv, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Subreddit", "Type", "Title", "URL", "Scraped_at"
            ])
            
            for subreddit_data in data:
                subreddit = subreddit_data["subreddit"]
                scraped_at = subreddit_data["scraped_at"]
                
                for topic in subreddit_data.get("python_topics", []):
                    writer.writerow([
                        subreddit,
                        topic['type'],
                        topic['title'],
                        "",
                        scraped_at
                    ])
                
                for discussion in subreddit_data.get("discussions", []):
                    writer.writerow([
                        subreddit,
                        discussion['type'],
                        discussion['title'],
                        discussion['url'],
                        scraped_at
                    ])
            
            print(f"All topics saved to files!")
        
    except Exception as e:
        print(f"ERROR: {e}")

# Main -> Execute the code above
def main() -> None:
    data = scrape_reddit()
    
    if data:
        print(f"Processing the data...")
        total_topics = 0
        total_discussions = 0
        
        for subreddit_data in data:
            topics_count = len(subreddit_data.get("python_topics", []))
            discussions_count = len(subreddit_data.get("discussions", []))
            
            total_topics += topics_count
            total_discussions += discussions_count
        
        print(f'\nTotal: {total_topics}: Python Topics, {discussions_count} Discussions')
        
        save_scraped_data(data)
    else:
        print("There is not data returned!")

if __name__ == "__main__":
    main()
