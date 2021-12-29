from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_pages(url, params):
    response = requests.request("GET", url, params=params)

    content = response.text
    soup = BeautifulSoup(content, features="html.parser")

    pages = soup.findAll("a", attrs={"class": "item"})
    page_nums = []
    for page in pages:
        try:
            page_nums.append(int(page.text))
        except ValueError:
            pass
    return page_nums


def remove_sub_string(string, sub):
    if string == "No display data":
        string = 0
    if string == "Contact For Price":
        string = 0
    if isinstance(string, (int, float)):
        return string
    return string.replace(sub, "")


def cleaned_df(df):
    df["Price"] = df["Price"].apply(remove_sub_string, args=("From",))
    df["Price"] = df["Price"].apply(remove_sub_string, args=("$",))
    df["Price"] = df["Price"].apply(remove_sub_string, args=(",",))
    df["Beds"] = df["Beds"].apply(remove_sub_string, args=("+",))
    df["Baths"] = df["Baths"].apply(remove_sub_string, args=("+",))
    df["Sizes"] = df["Sizes"].apply(remove_sub_string, args=(",",))
    df["Sizes"] = df["Sizes"].apply(remove_sub_string, args=("sqft",))

    df = df.astype({"Price": int, "Beds": int, "Baths": float, "Sizes": int})

    return df


def generate__dataframe(city):
    prices = []
    beds = []
    baths = []
    sizes = []
    addresses = []
    # driver.get('https://www.realtor.com/realestateandhomes-search/New-York_NY')

    # city = "Texas"
    csv_file = f"{city.lower()}_listings.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df = cleaned_df(df)
    else:
        url = "https://api.webscrapingapi.com/v1"
        uri = f"https://www.realtor.com/realestateandhomes-search/{city}"
        params = {"api_key": os.environ.get("API_KEY"), "url": uri}
        pages = get_pages(url, params)
        for page in range(1, pages[-1] + 1):
            if page == 1:
                params["url"] = uri
            else:
                params["url"] = f"{uri}/pg-{page}"
            response = requests.request("GET", url, params=params)

            content = response.text
            # print(content)
            soup = BeautifulSoup(content, features="html.parser")

            for element in soup.findAll(
                "li", attrs={"class": "component_property-card"}
            ):
                price = element.find("span", attrs={"data-label": "pc-price"})
                bed = element.find("li", attrs={"data-label": "pc-meta-beds"})
                bath = element.find("li", attrs={"data-label": "pc-meta-baths"})
                size = element.find("li", attrs={"data-label": "pc-meta-sqft"})
                address = element.find("div", attrs={"data-label": "pc-address"})

                if bed and bath:
                    nr_beds = bed.find("span", attrs={"data-label": "meta-value"})
                    nr_baths = bath.find("span", attrs={"data-label": "meta-value"})

                    # if nr_beds and float(nr_beds.text) >= 2 and nr_baths and float(nr_baths.text) >= 1
                    if nr_beds and nr_baths:
                        beds.append(nr_beds.text)
                        baths.append(nr_baths.text)

                        if price and price.text:
                            prices.append(price.text)
                        else:
                            prices.append("No display data")

                        if size and size.text:
                            sizes.append(size.text)
                        else:
                            sizes.append("No display data")
                        if address and address.text:
                            addresses.append(address.text)
                        else:
                            addresses.append("No display data")

        df = pd.DataFrame(
            {
                "Address": addresses,
                "Price": prices,
                "Beds": beds,
                "Baths": baths,
                "Sizes": sizes,
            }
        )
        df.to_csv(f"{city.lower()}_listings.csv", index=False, encoding="utf-8")
        df = cleaned_df(df)

    return df
