<?php
if (!empty($_GET)) {
    header("Location: manga_viewer.py?" . $_SERVER['QUERY_STRING']);
    die();
} else {
    include_once('./main_menu.html');
}
