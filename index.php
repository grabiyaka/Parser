<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>

<body>
    <?php
    require __DIR__ . "/phpQuery-onefile.php";



    // Создаем массив для хранения уникальных тегов
    // $uniqueTags = array();
    
    // Находим все теги на странице и добавляем их в массив
    // $tags = $pq->find('*');
    // foreach ($tags as $tag) {
    //     $tagName = $tag->tagName;
    
    //     // Проверяем, содержится ли тег уже в массиве
    //     if (!in_array($tagName, $uniqueTags)) {
    //         $uniqueTags[] = $tagName;
    //     }
    // }
    
    // // Выводим уникальные теги
    // foreach ($uniqueTags as $tag) {
    //     $array = $pq->find($tag);
    //     foreach ($array as $el) {
    //         $ent = pq($el);
    //         if ($ent->text() != '') {
    //             $data[$tag][] = $ent->text();
    //         }
    //     }
    // }
    // $titles_h2 = $pq->find('h2');
    // foreach ($titles_h2 as $title_h2) {
    //     $ent = pq($title_h2);
    //     if ($ent->text() != '') {
    //         $data['title_h2'][] = $ent->text();
    //     }
    // }
    
    // $titles_h4 = $pq->find('h4');
    // foreach ($titles_h4 as $title_h4) {
    //     $ent = pq($title_h4);
    //     if ($ent->text() != '') {
    //         $data['titles_h4'][] = $ent->text();
    //     }
    // }
    $categories = [
        'poliuretanovye-shtampy',
        'formy-dlya-3d-panelej',
        'dekorativnij-kamin',
        'formy-dlya-3d-blokov',
        'formy-dlya-dekora',
        'formy-dlya-sadovyh-figur',
        'master-shtampy'
    ];
    $products = [];
    $i = 0;
    foreach ($categories as $category) {
        $paginate = file_get_contents('https://formdekor.com/'.$category.'/');
        $paginate = phpQuery::newDocument($paginate);
        $paginate = $paginate->find('.pagination')->text();
        $paginate = str_split($paginate);
        $pages = [];
        foreach ($paginate as $page) {
            if ($page != '|' && $page != '<' && $page != '>') {
                $pages[] = $page;
            }
        }
        foreach ($pages as $page) {
            $file = file_get_contents('https://formdekor.com/'.$category.'/?page='.$page);
            $pq = phpQuery::newDocument($file);
            $data = [];
            $productsList = $pq->find('.products-category .products-list');
            $pqProducts = $productsList->find('.product-layout');

            foreach ($pqProducts as $key => $product) {
                $pqProduct = pq($product);
                $products[$i]['url'] = $pqProduct->find('a')->attr('href');
                $products[$i]['price'] = trim($pqProduct->find('.price-new')->text());
                $products[$i]['name'] = trim($pqProduct->find('a')->text());
                $images = array();
                $pqProduct->find('.product-card__gallery .item-img')->each(function ($item) use (&$images) {
                    $images[] = pq($item)->attr('data-src');
                });
                
                $products[$i]['images'] = $images;
                $products[$i]['category'] = $category;
                $i++;
            }
        }
        break;
    }


    echo '<pre>';
    print_r($products);
    echo '</pre>';

    function dd($value){
        echo '<pre>';
        print_r($value);
        echo '</pre>';
        die();
    }
    ?>
</body>

</html>