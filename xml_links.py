import xml.etree.ElementTree as ET
import requests

file_urls = [
    'https://gastrorag.ua/feed.xml',
    'https://wowshop.ua/index.php?route=extension/feed/ocext_feed_generator_yamarket&token=5287',
    'https://elektreka.com.ua/system/storage/download/v_nayavnost_yml.xml'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

combined_root = ET.Element('yml_catalog', date="2023-08-25 10:59")

shop_elem = ET.SubElement(combined_root, 'shop')
name_elem = ET.SubElement(shop_elem, 'name')
name_elem.text = "GASTRORAG.UA"

company_elem = ET.SubElement(shop_elem, 'company')
company_elem.text = "Gastrorag"

url_elem = ET.SubElement(shop_elem, 'url')
url_elem.text = "https://gastrorag.ua/"

currencies_elem = ET.SubElement(shop_elem, 'currencies')
currency_elem = ET.SubElement(currencies_elem, 'currency', id="UAH", rate="1")

categories_elem = ET.SubElement(shop_elem, 'categories')

offers_elem = ET.SubElement(shop_elem, 'offers')

for url in file_urls:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.content
        root = ET.fromstring(content)
        
        for offer_elem in root.findall(".//offer"):
            offers_elem.append(offer_elem)
        
        for category_elem in root.findall(".//category"):
            categories_elem.append(category_elem)
    else:
        print(f"Error fetching data from {url}. Status code: {response.status_code}")

combined_tree = ET.ElementTree(combined_root)
combined_tree.write('combined_output.xml', encoding='utf-8', xml_declaration=True)

print("Combined XML file has been created and saved.")
