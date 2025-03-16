from screener_scraper_base import ScreenerScraper

if __name__ == "__main__":
    scraper_smallcap = ScreenerScraper(
        base_url="https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3C+5000&page=",
        log_filename="SmallCap_screener_scraping.log",
        csv_filename="Small_Cap.csv",
        market_cap_type="SmallCap"
    )
    scraper_smallcap.run()