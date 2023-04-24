import csv
import datetime
import os
import requests
from bs4 import BeautifulSoup
import schedule
import time


def scrape_properties(url, csv_file):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    properties = soup.find_all("div", class_="p24_regularTile")

    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "price",
            "description",
            "bedrooms",
            "bathrooms",
            "parking",
            "pool",
            "listing_number",
            "property_type",
            "listing_date",
            "erf_size",
            "floor_size",
            "flatlet",
            "recent_sales_address",
            "recent_sales_price",
            "recent_sales_date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for prop in properties:
            price_tag = prop.find("div", class_="p24_price")
            if price_tag:
                price = price_tag.text.strip()
                price = float(price[1:].replace(",", ""))
            else:
                continue

            description = prop.find("span", class_="p24_content").text.strip()
            bedrooms = (
                prop.find("span", title="Bedrooms").text.strip()
                if prop.find("span", title="Bedrooms")
                else None
            )
            bathrooms = (
                prop.find("span", title="Bathrooms").text.strip()
                if prop.find("span", title="Bathrooms")
                else None
            )
            parking = (
                prop.find("span", title="Parking Spaces").text.strip()
                if prop.find("span", title="Parking Spaces")
                else None
            )
            pool = True if prop.find("span", title="Pool") else False
            listing_number = prop["data-listing-number"]
            property_type = prop.find("div", class_="p24_propertyType").text.strip()
            listing_date = prop.find("div", class_="p24_listingDate").text.strip()

            # Extract additional details
            detail_items = prop.find_all("span", class_="p24_featureDetails")
            erf_size, floor_size, flatlet = None, None, False
            for detail in detail_items:
                if "Erf Size" in detail.text:
                    erf_size = detail.text.strip().split(" ")[-1]
                elif "Floor Size" in detail.text:
                    floor_size = detail.text.strip().split(" ")[-1]
                elif "Flatlet" in detail.text:
                    flatlet = True

            # Extract recent sales data
            recent_sales_address, recent_sales_price, recent_sales_date = (
                None,
                None,
                None,
            )
            if prop.find("div", class_="p24_recentListing"):
                recent_sales_address = (
                    prop.find("div", class_="p24_recentListing")
                    .find("div", class_="p24_location")
                    .text.strip()
                )
                recent_sales_price = float(
                    prop.find("div", class_="p24_recentListing")
                    .find("div", class_="p24_price")
                    .text.strip()[1:]
                    .replace(",", "")
                )
                recent_sales_date = (
                    prop.find("div", class_="p24_recentListing")
                    .find("div", class_="p24_listingDate")
                    .text.strip()
                )

            writer.writerow(
                {
                    "price": price,
                    "description": description,
                    "bedrooms": bedrooms,
                }
            )


def scrape_recent_sales(url, csv_file):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    sales_items = soup.find_all("div", class_="p24_recentSalesItem")

    with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["address", "last_sold_price", "last_sold_date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for item in sales_items:
            address = item.find("div", class_="p24_location").text.strip()
            last_sold_price = float(
                item.find("div", class_="p24_price").text.strip()[1:].replace(",", "")
            )
            last_sold_date = item.find("div", class_="p24_listingDate").text.strip()

            writer.writerow(
                {
                    "address": address,
                    "last_sold_price": last_sold_price,
                    "last_sold_date": last_sold_date,
                }
            )


def main():
    url = "https://www.property24.com/for-sale/kuils-river/western-cape/870?sp=pt%3d2000000"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = "C:\\Users\\Bradwyn\\Desktop\\PropertyUpdate\\"
    csv_file = f"{folder_path}property_update({timestamp}).csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "price",
            "description",
            "bedrooms",
            "bathrooms",
            "parking",
            "pool",
            "listing_number",
            "property_type",
            "listing_date",
            "erf_size",
            "floor_size",
            "flatlet",
            "recent_sales_address",
            "recent_sales_price",
            "recent_sales_date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    scrape_properties(url, csv_file)


if __name__ == "__main__":
    main()
