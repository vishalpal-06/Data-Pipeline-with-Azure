from screener_scraper_base import ScreenerScraper

if __name__ == "__main__":
    scraper_midcap = ScreenerScraper(
        base_url="https://www.screener.in/screen/raw/?sort=&order=&source_id=&query=Market+Capitalization+%3E%3D+5000+AND+Market+Capitalization+%3C+20000&page=",
        log_filename="MidCap_screener_scraping.log",
        csv_filename="Mid_Cap.csv",
        market_cap_type="MidCap"
    )
    scraper_midcap.run()