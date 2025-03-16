from screener_scraper_base import ScreenerScraper

if __name__ == "__main__":
    scraper_largecap = ScreenerScraper(
        base_url="https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3E%3D+20000&page=",
        log_filename="LargeCap_screener_scraping.log",
        csv_filename="Large_Cap.csv",
        market_cap_type="LargeCap"
    )

    scraper_largecap.run()