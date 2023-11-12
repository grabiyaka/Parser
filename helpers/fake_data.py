def generate_fake_data():
    names = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    prices = ['10.99', '24.99', '35.00', '15.49', '19.99']
    descriptions = ['Description A', 'Description B', 'Description C', 'Description D', 'Description E']
    picture_urls = ['url1.jpg', 'url2.jpg', 'url3.jpg', 'url4.jpg', 'url5.jpg']

    fake_data = []
    for _ in range(10):
        product = {
            'name': random.choice(names),
            'price': random.choice(prices),
            'description': random.choice(descriptions),
            'pictures': [random.choice(picture_urls) for _ in range(random.randint(1, 5))],
            'url': 'https://example.com/products/' + str(random.randint(1, 100))
        }
        fake_data.append(product)
    
    return fake_data