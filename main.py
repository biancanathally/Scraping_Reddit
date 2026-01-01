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
                "subreddit": subreddit_name,
                "url": url,
                "title": soup.title.string if soup.title else "No title",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
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

                # URL FIX: Transform '/r/...' into 'https://reddit.com/r/...'
                if href.startswith("/"):
                    full_url = f"https://www.reddit.com{href}"
                else:
                    full_url = href

                # Verify if it's a comments link and has a title
                if (
                    text
                    and len(text) > 5
                    and "/comments/" in full_url
                    and full_url not in seen_urls
                ):
                    seen_urls.add(full_url)

                    print(f"Downloading comments from: {text[:30]}...")

                    # Call the function that gets comments
                    comments_list = get_comments_from_url(full_url)

                    discussions.append(
                        {
                            "title": text[:100],
                            "url": full_url,
                            "type": "discussion",
                            "comments_count": len(comments_list),
                            "comments": comments_list
                        }
                    )

                    # To avoid rate limiting by Reddit
                    time.sleep(2)

            subreddit_data["python_topics"] = topics
            subreddit_data["discussions"] = discussions

            all_data.append(subreddit_data)
            time.sleep(2)

        except Exception as e:
            print(f"ERROR: {e}")

    return all_data


def get_comments_from_url(url: str) -> list[str]:
    # Change 'www' to 'old'
    # This ensures we get static HTML that BeautifulSoup can parse
    if "www.reddit.com" in url:
        url = url.replace("www.reddit.com", "old.reddit.com")

    headers = {
        # We use a generic User-Agent to avoid being blocked
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    try:
        print(f"   Reading: {url}...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, "html.parser")

        comments = []

        # Old Reddit selector
        # In the old site, comments are inside div.entry -> div.usertext-body
        # The 'commentarea' is the general comments area
        comment_area = soup.find("div", class_="commentarea")

        if comment_area:
            # We get all the text bodies inside the comments area
            for comment_div in comment_area.find_all("div", class_="usertext-body"):
                text = comment_div.get_text(strip=True)

                # Basic cleaning filters
                if text and text not in ["[deleted]", "[removed]"]:
                    comments.append(text)

        return comments

    except Exception as e:
        print(f"   Error reading comments: {e}")
        return []


# Function -> Save scraped data (Both JSON and CSV formats)
def save_scraped_data(
    data, filename_json="python_topics.json", filename_csv="python_topics.csv"
):
    if not data:
        print(f"No data to save.")
        return

    current_dir = Path(__file__).parent.absolute()

    path_json = current_dir / filename_json
    path_csv = current_dir / filename_csv

    # JSON
    try:
        with open(path_json, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=True)
        print(f"Python topics saved: {filename_json}")
    except Exception as e:
        print(f"ERROR: {e}")

    # CSV
    try:
        with open(path_csv, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Subreddit", "Type", "Title", "URL", "Scraped_at"])

            for subreddit_data in data:
                subreddit = subreddit_data["subreddit"]
                scraped_at = subreddit_data["scraped_at"]

                for topic in subreddit_data.get("python_topics", []):
                    writer.writerow(
                        [subreddit, topic["type"], topic["title"], "", scraped_at]
                    )

                for discussion in subreddit_data.get("discussions", []):
                    writer.writerow(
                        [
                            subreddit,
                            discussion["type"],
                            discussion["title"],
                            discussion["url"],
                            scraped_at
                        ]
                    )

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

        print(
            f"\nTotal: {total_topics}: Python Topics, {discussions_count} Discussions"
        )

        save_scraped_data(data)
    else:
        print("There is not data returned!")


if __name__ == "__main__":
    main()
