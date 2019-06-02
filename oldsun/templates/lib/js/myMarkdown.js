// base : jquery , marked
MD_TESTMODE=false;
dev=false;
var isDefined=(typeof marked != "undefined" ? true : false);
//if(isDefined){
    marked.setOptions({
        renderer: new marked.Renderer(),
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: false,
        smartLists: true,
        smartypants: false,
        highlight: function (code,lang) {
            return hljs.highlightAuto(code,[lang]).value;
        }
    });
//    }
function myMarked(text){
    // remove <div></div>
    log(text)
    if(dev){log('myMarkdown source:');log(text)}
    text=text.replaceAll('</div><div>','\n');
    text=text.replaceAll('<div>','\n');
    text=text.replaceAll('</div>','\n');
    text=escapeToHTML(text);
//    log('escapedHTML:');log(text)
    md=marked(text);dev=true;
    var ta=document.createElement('textarea');ta=$(ta);
    ta.html(md);md=ta.val();
    if(dev){log('myMarkdown result:');log(md);}
    return md;
}
function parseMarkdown(sel_show_box){
    mks=$(sel_show_box);
    for(var i=0;i<mks.length;i++){
        mk=$(mks[i]);
        selector='#'+mk[0].id;
        //log('mk.id:'+mk.id);
        sel_data_box='#'+mk[0].getAttribute('data-box-id');
        mk.html(myMarked(String(getData(sel_data_box)))    );
    }
    mks.addClass('rich-text');
}
function initMarkdown(){
    parseMarkdown('.markdown');
}