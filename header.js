div = document.getElementById('manga_ddl_topbar');
if (!div){
    var div = document.createElement('div');
    div.id = 'manga_ddl_topbar';
    document.body.prepend(div);

    var style = document.createElement('style');
    style.innerHTML = '.highlight { background-color: #1010D0; } .selected { background-color: #0000A0; }';
    document.getElementsByTagName('head')[0].appendChild(style);
}
div.innerHTML = arguments[0].trim(); // arguments[0] - Topbar HTML

function getXPathForElement(element) { // Stackoverflow
    const idx = (sib, name) => sib 
        ? idx(sib.previousElementSibling, name||sib.localName) + (sib.localName == name)
        : 1;
    const segs = elm => !elm || elm.nodeType !== 1 
        ? ['']
        : elm.id && document.getElementById(elm.id) === elm
            ? [`id("${elm.id}")`]
            : [...segs(elm.parentNode), `${elm.localName.toLowerCase()}[${idx(elm)}]`];
    return segs(element).join('/');
}

var xPath_field = document.getElementById('manga_ddl_id');
var base_url = 'http://127.0.0.1:' + arguments[1] // arguments[1] - Local port

var highlighted = null;
var selected = null;

window.addEventListener('mousemove', (event) => {
    if (highlighted != null){
        highlighted.classList.remove("highlight");
    }
    if (div.contains(event.target)){
        return;
    }
    highlighted = event.target;
    highlighted.classList.add("highlight");
});


window.addEventListener('click', (event) => {
    if (div.contains(event.target)){
        return;
    }
    if (selected != null){
        selected.classList.remove("selected");
    }
    selected = event.target;
    selected.classList.add("selected");
    xPath_field.innerHTML = getXPathForElement(selected);
});

document.getElementById("submit_manga_xpath_btn").addEventListener("click", submit_manga_xpath);
function submit_manga_xpath (e) {
    if (selected != null){
        selected.classList.remove("selected");
    }else{
        return;
    }
    if (highlighted != null){
        highlighted.classList.remove("highlight");
    }

    url = base_url + getXPathForElement(selected);
    
    req = new XMLHttpRequest();
    req.open('GET', url);
    req.send();
}