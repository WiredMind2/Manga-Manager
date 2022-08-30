function get(url, parsed = true) {
    return fetch(url, {
        method: 'GET',
        mode: 'no-cors',
    }).then(function(response) {
        if (parsed) {
            return response.json();
        } else {
            return response.text();
        }
    }).then(function(data) {
        return data;
        // }).catch(function(err) {
        //     console.log("Error in get: " + err);
        //     return err
    });
}

function post(url, data, parsed = true) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        mode: 'no-cors',
        body: JSON.stringify(data)
    }).then(function(response) {
        if (parsed) {
            return response.json();
        } else {
            return response.text();
        }
    }).then(function(data) {
        return data;
        // }).catch(function(err) {
        //     console.log("Error in post: " + err);
        //     return err
    });
}

function start() {
    get('?action=start').then(function(data) {
        if (data == "Ok") {
            is_stopped = false;
            update_logs();
        } else {
            console.log('Error while starting: ' + data);
        }
    })
}

function stop() {
    get('?action=stop').then(function(data) {
        is_stopped = true;
        if (data != "Ok") {
            console.log('Error while stopping: ' + data);
        }
    })
}

function download() {
    data = JSON.parse('[{"url": "https://readmanganato.com/manga-mh989642", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ax951880", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-je987087", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ci980191", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-bf979214", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ej981992", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-eu982203", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-to970571", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-cb980036", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ec981811", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-em981495", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ie985687", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-va953509", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ko987549", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-hu985229", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-ex982080", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-gt984176", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-gi983617", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-dg980989", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-bt978676", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-fr982926", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}, {"url": "https://readmanganato.com/manga-dk980967", "title": "/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1", "xpth": {"main_list": "/html/body/div[1]/div[3]/div[1]/div[3]/ul", "main_list_item": "a", "img_list": "/html/body/div[1]/div[3]", "img_list_item": "img"}, "img_url": "src", "img_desc": "alt", "headers": {"Referer": "https://readmanganato.com/"}}]')
    post('?action=download', data = data).then(function(data) {
        if (data != "Ok") {
            console.log('Error while starting: ' + data);
        }
    })
}

function update_logs() {
    parse_logs();

    if (!is_stopped) {
        setTimeout(update_logs, 5000);
    }
}

function add_log(log) {
    log_status = Status.from_id(log[0]);
    state = states[log_status]

    switch (log_status) {
        case Status.DOWNLOAD:
            title = log[1];

            if (!state['titles'].includes(title)) {
                state['count']++;
                state['titles'].push(title);
            }

            break;

        case Status.PARSE:
            url = log[1];
            level = log[2];

            if (level == -1) {
                delete state[url];
                state['count']--;

            } else {
                if (!(url in state)) {
                    state['count']++;
                }
                state[url] = level;
            }

            break;

        case Status.LINKS:
            url = log[1];
            level = log[2];

            if (level == -1) {
                delete state[url];
                state['count']--;

            } else {
                if (!(url in state)) {
                    state['count']++;
                }
                state[url] = level;
            }

            break;

        case Status.IMAGES:
            mainpage_url = log[1];
            img_url = log[2];

            // TODO

            break;
    }
}

function get_manga_cell(url) {
    if (url in manga_cells) {
        return manga_cells[url];
    } else {
        return false;
    }
}

function create_manga_cell(url) {

    if (get_manga_cell(url) !== false) {
        // Cell already exists
        return;
    }

    const parent = document.getElementById('manga_list');

    const cell = document.getElementById('cell_template').content.cloneNode(true);

    cell.querySelector('#cell_template_title').innerText = url;

    manga_cells[url] = cell;

    parent.appendChild(cell);
}

function destroy_manga_cell(url) {
    let cell = get_manga_cell(url);
    if (cell === false) {
        // Cell do not exists
        return;
    }

    delete manga_cells[url];
    cell.remove();
}

function update_bar(cell, id, progress) {
    console.log(id, '#' + id, cell.querySelector('#' + id));
    cell.querySelector('#' + id).value = progress;
    cell.querySelector('#' + id).innerText = progress + '%';
}