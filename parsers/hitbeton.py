from settings import HTMLSession, id, score

def getHitbetonData():
    global score
    categories = [
        'tvaryny',
        'ptakhy',
        'anhely',
        'liudy',
        'fentezi',
        'kashpo',
        'baliasyny-altanky-ta-inshe',
        'rizne'
    ]
    products = []
    i = 0
    productsList = []
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0',
        'referer': 'https://hitbeton.com.ua/',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '_gcl_au=1.1.1382130868.1692686260; _ga=GA1.1.1438058064.1692686260; _ga_9TN454D01M=GS1.1.1692716581.4.0.1692716598.0.0.0',
        'accept-charset': 'utf-8'
    }

    session = HTMLSession()

    for category_index, category in enumerate(categories):
        num_page = 1
        while True: 
            num_product = 1
            url = 'https://hitbeton.com.ua/product-category/' + category + '/page/' + str(num_page) + '/'
            response = session.get(url)
            if response.status_code == 200:
                page = response.html
                product_links = page.find('.products a')
                for link in product_links:
                    products_request = session.get(link.attrs['href'])
                    if products_request.status_code == 200:
                        product_page = products_request.html
                        product_data = {}
                        
                        product_data['url'] = link.attrs['href']
                        
                        description_element = product_page.find('.woocommerce-Tabs-panel--description p', first=True)
                        if description_element:
                            product_data['description'] = description_element.text
                        else:
                            product_data['description'] = ''

                        name_element = product_page.find('.product_title', first=True)
                        if name_element:
                            product_data['name'] = name_element.text
                        else:
                            product_data['name'] = ''

                        price_element = product_page.find('.woocommerce-Price-amount bdi', first=True)
                        if price_element:
                            product_data['price'] = price_element.text.split()[0]
                        else:
                            product_data['price'] = ''

                        picture_elements = product_page.find('figure .woocommerce-product-gallery__image a')
                        pictures = [picture.attrs['href'] for picture in picture_elements]
                        if pictures:
                            product_data['pictures'] = pictures
                        else:
                            product_data['pictures'] = []

                        
                        products.append(product_data)
                        print(f'hitbeton: product: {num_product}/{len(product_links)}, page: {num_page}, category: {category_index + 1}/{len(categories)}')
                        num_product = num_product + 1
                        score = score + 1
                        
                    
                num_page = num_page + 1
            else: break
          
    print('Hitbeton done!')
    return products


def generate_xml_h(products, article):
    global id
    output = ''
    for index, product in enumerate(products):
        output += '<offer id="' + str(id) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>UAH</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + 'hitbeton' + '</vendor>\n' \
                  '        <vendorCode>' + str(id) + ' ' + article + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>''</keywords>\n' \
                  '        <country>Украина</country>\n' \

        for image in product['pictures']:
            output += '<picture>' + image + '</picture>'
        output += '</offer>'
        id = id + 1
    return output