
//  输出来源为 contenteditable 输出markdown


function renderSelect(sel){
   var v=sel.attr('value');
   var ch=sel.children();
//   log(v)
   for(var i=0;i<ch.length;i++ ){
        var op=$(ch[i]);
        var val=op.val();
        if(val===v)op[0].selected=true;
   }
}
function renderEditor(app){
   var is_public=app.find('#is_public');
   var type=app.find('#type');
   renderSelect(is_public);
   renderSelect(type);

}
function toBool(data){
    if(data==='true'||data==='1')return true;
    else if(data==='false'||data==='0')return false;

}
function getLabel(el){
    var list=el.find('#label-list');
    var children=list.children();
    var label=[];
    for(var i=0;i<children.length;i++){
        l=$(children[i]).text();
        label.push(l);
    }
    label=label.join('&&');
//    log(label);
    return label;

}
function initLabelApp(app){
    var area=app.find('#label-area');
    var input=area.find('#label-input');
    var assure=area.find('#label-input-assure');
    var list=area.find('#label-list');
    function assureInput(){
        var label=input.val();
        var li=`<li class='label-entry f-left'><span class="label label-primary" >${label}</span></li>`;
        list.append(li);
        input.val('');
        hide(assure);
    }
    input.on('input propertychange',(e)=>{
        show(assure);
    });
    input.keydown((e)=>{
        if(e.keyCode==13)assureInput();
    })
    assure.click(()=>{
        assureInput();
    });
}
function initPreviewSwitch(el){
    var btns=el.find('.switch-preview');
    var input=el.find('#input');
    var output=el.find('#output');
    btns.map((n,btn)=>{
        var b=$(btn);
        var s=new Switch(b,()=>{if(screen.width<400)hide(input);},()=>{if(screen.width<400)show(input);});
    });
}
function initEditor(){
    var app=$('#editor_app');
    var title=app.find('#title');
    var input=app.find('#input');
    var output=app.find('#output');
    var summary=app.find('#summary-area');
    var is_public=app.find('#is_public');
    var type=app.find('#type');
    var label_area=app.find('#label-area');
    initLabelApp(app);
    renderEditor(app);
    initPreviewSwitch(app);
    var md=myMarked(input.html());
//    log('md:');log(md);log(hi)
    output.html(md);
    input.on('focus input propertychange',()=>{
    //  transfer to markdown
//        text=input.text();
//        log('plain:  *******');log(text);
        html=input.html();
//        log('html:  *******');log(html)
        md=myMarked(html);
//        log('md: ********');log(md);
        output.html(md);
    });
    var edit=false;
    if(app.attr('edit')=='true')edit=true;
    var submit=app.find('#submit');
    var message=$('#message');

    submit.click(()=>{
//        log(title.text().trim())
        // 检查
        if (title.html()==='')return;
        blog={
            blog_heading:title.text().trim(),
            blog_summary:summary.html().trim(),
            blog_content:input.html().trim(),
            is_public:toBool(is_public.val()),
            type:type.val(),
            label:getLabel(label_area)
        }
            log(blog);
        if(edit){
            blog_id=app.attr('blog_id');
            ret=$.post({url:'/me/editor/'+blog_id,data:JSON.stringify(blog),async:false}).responseJSON;
            }
        else ret=$.post({url:'/me/post_blog',data:JSON.stringify(blog),async:false}).responseJSON;
        message.html(ret.message);
        show(message);
    })
}

$(document).ready(function(){
    initEditor();
})