from settings import BeautifulSoup, requests, id, score

def getFormdekorData():
    global score
    categories = [
        'poliuretanovye-shtampy',
        'formy-dlya-3d-panelej',
        'dekorativnij-kamin',
        'formy-dlya-3d-blokov',
        'formy-dlya-dekora',
        'formy-dlya-sadovyh-figur',
        'master-shtampy'
    ]
    products = []

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0',
        'referer': 'https://formdekor.com/',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'OCSESSID=077481e943b5ef1531aeda1f01; _ga=GA1.1.1198526705.1687263981; language=ru-ru; currency=USD; sorecentproduct=109%2C149%2C115%2C162%2C50%2C118%2C177; _ga_BRFVKH6K7T=GS1.1.1690027036.31.0.1690027036.0.0.0',
        'Host': 'formdekor.com'
    }

    session = requests.Session()
    session.headers.update(headers)

    for category_index, category in enumerate(categories):
        url = 'https://formdekor.com/' + category + '/'
        response = session.get(url)

        if response.status_code == 200:
            paginate = response.text
            soup = BeautifulSoup(paginate, 'html.parser')
            paginate_element = soup.select_one('.pagination')
            if(paginate_element):
                paginate_text = paginate_element.get_text()
            else:
                paginate_text = ['1']
            pages = [page for page in paginate_text if page not in '|<>']

            for page in pages:
                url = 'https://formdekor.com/' + category + '/' + '?page=' + page
                response = session.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    productsList = soup.select(
                        '.products-category .products-list .product-layout')
                    num_product = 1
                    for product in productsList:
                        product_data = {}
                        pqProduct = BeautifulSoup(str(product), 'html.parser')
                        product_data['url'] = pqProduct.find('a')['href']
                        product_data['price'] = pqProduct.select_one(
                            '.price-new').get_text().replace('$', '').strip()

                        nameDiv = pqProduct.select_one('h4 a')
                        product_data['name'] = nameDiv.get_text().strip()
                        product_data['category'] = category

                        productPageUrl = product_data['url']
                        response = session.get(productPageUrl.strip())
                        if response.status_code == 200:
                            productPage = response.text
                            pqProductPage = BeautifulSoup(
                                productPage, 'html.parser')
                            product_data['brand'] = pqProductPage.select_one(
                                '.brand a span').get_text().strip()

                            modelDiv = pqProductPage.select_one('.model')
                            product_data['model'] = modelDiv.get_text().strip()

                            product_data['material'] = pqProductPage.select_one(
                                '.propery-title').get_text().strip() if pqProductPage.select_one('.propery-title') else ''

                            product_data['description'] = pqProductPage.select_one(
                                '#collapse-description').get_text().strip()

                            keyWords = [kw.get_text().strip()
                                        for kw in pqProductPage.select('#tab-tags a')]
                            product_data['key_words'] = keyWords

                            images = [img['data-image']
                                      for img in pqProductPage.select('.image-additional a')]
                            product_data['images'] = images

                            address_element = pqProductPage.select_one(
                                '.adres')
                            if address_element:
                                product_data['address'] = address_element.get_text(
                                ).strip()
                            else:
                                product_data['address'] = ''

                        products.append(product_data)
                        print(f'formdekor: product: {num_product}/{len(productsList)}, page: {page}/{len(pages)} category: {category_index + 1}/{len(categories)}')
                        num_product = num_product + 1
                        score = score + 1

    print('Formdekor done!')
    return products

def generate_xml_f(products):
    global id
    output = ''

    for index, product in enumerate(products):
        output += '<offer id="' + str(id) + '" available="true">\n' \
                  '        <url>' + product['url'] + '</url>\n' \
                  '        <price>' + product['price'] + '</price>\n' \
                  '        <currencyId>USD</currencyId>\n' \
                  '        <categoryId></categoryId>\n' \
                  '        <quantity_in_stock></quantity_in_stock>\n' \
                  '        <name>' + product['name'] + '</name>\n' \
                  '        <vendor>' + product['brand'] + '</vendor>\n' \
                  '        <vendorCode>' + product['model'] + '</vendorCode>\n' \
                  '        <description><![CDATA[' + product['description'] + ']]></description>\n' \
                  '        <keywords>'
        for key, word in enumerate(product['key_words']):
            if word != product['key_words'][-1]:
                output += word + ', <br/>'
            else:
                output += word
        output += '</keywords>\n' \
                  '        <country>Украина</country>\n' \
                  '        <param name="Матеріал">' + product['material'] + '</param>\n' \
                  '        <param name="Бренд">' + \
            product['brand'] + '</param>\n'

        for image in product['images']:
            output += '<picture>' + image + '</picture>'
        output += '</offer>'
        id = id + 1
    return output