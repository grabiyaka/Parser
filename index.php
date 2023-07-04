<?php
set_time_limit(2000);
ini_set('display_errors', 0);
// if (date('H:i') === '10:00') {
    require __DIR__ . "/phpQuery-onefile.php";
    require __DIR__ .  "/functions.php";
    require __DIR__ .  "/parsers/formdekor.php";
    require __DIR__ .  "/parsers/techno-odis.php";
    $formdekorData = getFormdekorData();
    file_put_contents('xml/formdekor.xml', $formdekorData);
    $technoOdisData = getTechnoOdisData();
    file_put_contents('xml/techno-odis.xml', $technoOdisData);
// }