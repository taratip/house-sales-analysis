from lxml import html
import requests
import unicodecsv as csv
import argparse
import json


def parse(page):
    if page == "1_p":
        url = "https://www.zillow.com/homes/recently_sold/Boston-MA/house,condo,apartment_duplex,townhouse_type/44269_rid/lot_sort/42.447781,-70.827828,42.179179,-71.267281_rect/10_zm/"
    else:
        url = "https://www.zillow.com/homes/recently_sold/Boston-MA/house,condo,apartment_duplex,townhouse_type/44269_rid/lot_sort/42.447781,-70.827828,42.179179,-71.267281_rect/10_zm/{0}/".format(
            page)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    parser = html.fromstring(response.text)
    search_results = parser.xpath("//div[@id='search-results']//article")

    properties_list = []

    for properties in search_results:
        comment_data = properties.xpath(".//div[@class='minibubble template hide']//comment()")
        data = str(comment_data)[5:-4]
        data1 = data.replace("\\\\", "")
        data1 = data1.replace("\-", "-")

        data_dict = json.loads(data1)

        bedroom = data_dict['bed']
        bathroom = data_dict['bath']
        title = data_dict['title']

        if 'homeInfo' in data_dict:
            address = data_dict['homeInfo']['streetAddress'] if 'streetAddress' in data_dict['homeInfo'] else None
            city = data_dict['homeInfo']['city'] if 'city' in data_dict['homeInfo'] else None
            state = data_dict['homeInfo']['state'] if 'state' in data_dict['homeInfo'] else None
            zipcode = data_dict['homeInfo']['zipcode'] if 'zipcode' in data_dict['homeInfo'] else None
            price = data_dict['homeInfo']['price'] if 'price' in data_dict['homeInfo'] else None
            date_sold = data_dict['homeInfo']['dateSold'] if 'dateSold' in data_dict['homeInfo'] else None
            living_area = data_dict['homeInfo']['livingArea'] if 'livingArea' in data_dict['homeInfo'] else None
            year_bulit = data_dict['homeInfo']['yearBuilt'] if 'yearBuilt' in data_dict['homeInfo'] else None
            lot_size = data_dict['homeInfo']['lotSize'] if 'lotSize' in data_dict['homeInfo'] else None
            home_type = data_dict['homeInfo']['homeType'] if 'homeType' in data_dict['homeInfo'] else None
            home_status = data_dict['homeInfo']['homeStatus'] if 'homeStatus' in data_dict['homeInfo'] else None
        else:
            address = None
            city = None
            state = None
            zipcode = None
            price = None
            date_sold = None
            living_area = None
            year_bulit = None
            lot_size = None
            home_type = None
            home_status = None

        properties = {
            'title': title,
            'address': address,
            'city': city,
            'state': state,
            'zipcode': zipcode,
            'price': price,
            'date_sold': date_sold,
            'bedrooms': bedroom,
            'bathrooms': bathroom,
            'living_area': living_area,
            'lot_size': lot_size,
            'year_bulit': year_bulit,
            'home_type': home_type,
            'home_status': home_status
        }

        properties_list.append(properties)

    return properties_list


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('page', help='')
    args = argparser.parse_args()
    page = args.page
    print("Fetching data for %s" % (page))
    scraped_data = parse(page)
    print("Writing data to output file")
    with open("properties-%s.csv" % (page), 'wb')as csvfile:
        fieldnames = ['title', 'address', 'city', 'state', 'zipcode',
                      'price', 'date_sold', 'bedrooms', 'bathrooms', 'living_area', 'lot_size', 'year_bulit', 'home_type', 'home_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in scraped_data:
            writer.writerow(row)
