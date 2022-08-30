const states = {};
const manga_cells = {};
let is_stopped = true;
const status_keys = ['DOWNLOAD', 'PARSE', 'LINKS', 'IMAGES'];

// DOWNLOAD - (Status.DOWNLOAD, url, title)
// PARSE - (Status.PARSE, url, level)
// LINKS - (Status.LINKS, url, level)
// IMAGES - (Status.IMAGES, mainpage url, image url)


function init() {
    for (var idx = 0; idx++; idx < Status.keys.Count()) {
        value = status_keys[idx];
        // Status[key] = value;
        states[value] = { 'count': 0 };
    }
}

init();