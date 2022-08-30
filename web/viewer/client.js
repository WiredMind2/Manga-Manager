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

function getMangas() {
    get('./?action=manga_list').then(function(data) {
        for (let manga of data) {
            addMangaRow(manga);
        }
    })
}

function addMangaRow(manga) {
    const parent = document.getElementById('manga_list');

    const cell = document.getElementById('cell_template').content.cloneNode(true);

    cell.querySelector('#cell_template_link').href = manga['url'];
    cell.querySelector('#cell_template_title').innerText = manga['title'];
    cell.querySelector('#cell_template_img').src = manga['picture'];
    cell.querySelector('#cell_template_chapters').innerText = manga['chapters_count'];

    parent.appendChild(cell);
}

function getMangaInfo(manga) {
    get('?action=get_manga_info&manga=' + manga).then(function(data) {
        console.log(data);

        const title = document.getElementById('manga_title');
        title.innerText = data['title'];

        const parent = document.getElementById('manga_data');
        const template = document.getElementById('chapter_template').content;

        for (let idx = 1; idx <= data['chapters']; idx++) {
            let chapter = template.cloneNode(true);

            let link = chapter.querySelector('#chapter_template_link');
            link.href = '?action=get_chapter&manga=' + manga + '&chapter=' + idx;
            link.innerText = 'Chapter ' + idx;

            parent.appendChild(chapter);
        }
    })
}

function setupReader(title, chapter, img_count) {
    const parent = document.getElementById('manga_reader');
    const template = document.getElementById('image_template').content;

    for (let idx = 1; idx <= img_count; idx++) {
        let element = template.cloneNode(true);

        let img = element.querySelector('#image_template_img');
        img.src = '?action=get_image&manga=' + title + '&chapter=' + chapter + '&image=' + idx;

        parent.appendChild(element);
    }
}