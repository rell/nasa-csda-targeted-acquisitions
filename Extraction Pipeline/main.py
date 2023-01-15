from multiprocessing import freeze_support
from src.scraper import load_sources
from src.orders_extractor import get_bulk_orders
from src.location_recognizer import LocationExtractor
from src.order import run_ordering, check_order_status
from src.csv_creator import create_csv


if __name__ == "__main__":
    freeze_support()
    sources = load_sources(r"scrape_urls/scrape_urls.txt")
    extractor = LocationExtractor(
        in_file="output/output.json",
        out_locations="locations.json",
        out_coordinates="coordinates.json",
        html_output_file="visualizations.html",
        out_csv_file="output.csv"
    )
    extractor.extract()

    get_bulk_orders("locations.json", out_folder="orders")
    create_csv(in_folder="orders", out_csv="orders.csv")
    run_ordering()