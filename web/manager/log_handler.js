function parse_logs() {
    get('?action=logs').then(function(data) {
        for (let log of data) {
            const status = status_keys[log[0] - 1];
            switch (status) {
                case 'DOWNLOAD':
                    url = log[1];
                    title = log[2];

                    log_download(url, title);

                    break;

                case 'PARSE':
                    url = log[1];
                    level = log[2];

                    log_parse(url, level);

                    break;

                case 'LINKS':
                    url = log[1];
                    level = log[2];

                    log_links(url, level);

                    break;

                case 'IMAGES':
                    mainpage_url = log[1];
                    img_url = log[2];

                    log_images(mainpage_url, img_url);

                    break;
            }
        }
    });
}

function log_download(url, title) {

}

function log_parse(url, level) {

    if (level == 0) {
        create_manga_cell(url);
    } else if (level == -1) {
        return destroy_manga_cell(url);
    }

    let cell = get_manga_cell(url);
    update_bar(cell, 'progress_parsing', level * 100 / 3)
}

function log_links(url, level) {

}

function log_images(mainpage_url, img_url) {

}