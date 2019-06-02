function log(text){console.log(text);}
function initMarked(){
  var myMarked = marked;
  myMarked.setOptions({
  renderer: new myMarked.Renderer(),
  highlight: function(code) {
    return hljs.highlightAuto(code).value;
  },
  pedantic: false,
  gfm: true,
  tables: true,
  breaks: false,
  sanitize: false,
  smartLists: true,
  smartypants: false,
  xhtml: false
    });
}
class FaceManager{
    constructor(selector){
        this.selector=selector;
        this.el=$(selector);
        this.mode='none';
    }
    setMode(mode){
        this.mode=mode;
        this.executeMode();
    }
    closeMode(){
        this.el.removeClass('mode-dark');
    }
    executeMode(){
        this.el.addClass(this.mode);
    }
}
function copyHtml(src,tar){
    var head=getHead(tar.val());
    var format=head.format;
    if(format=='md'||format=='markdown')return;
    var html=src.html();
    tar.val(html);
}
function renderText(text){
    var head;var body;
    [head,body]=getHeadAndBody(text);
    if(!head)return text;
    var dic=head.strip('/*').strip('*/').toDict(';');
    if(!dic.hasOwnProperty('format'))dic.format='text/plain';
    var format=dic.format;
    if(format=='markdown' || format=='md')return marked(body);
    return body;
}

function getHead(text){
    var head;var body;
    [head,body]=getHeadAndBody(text);
    if(!head)return {};
    var dic=head.strip('/*').strip('*/').toDict(';');log(dic);
    if(!dic.hasOwnProperty('format'))dic.format='text/plain';
    return dic;
}
function copyText(src,tar){
    var text=src.val();
    text=renderText(text);
    tar.html(text);
}
class Editor{
    constructor(selector){
        var el=$(selector);
        this.selector=selector;
        this.el=el;
        this.text_input=el.find('#text-input');
        this.html_input=el.find('#html-input');
        this.title_input=el.find('#title-input');
        this.cate_input=el.find('#cate-input');
        this.tags_input=el.find('#tags-input');
        this.msg_box=$('.msg-box-tem');
        this.mode='create';this.submit_url='/manage/editor';
    }
    editBlog(blog,mode='alter'){
        this.mode=mode;
        this.text_input.val(blog.text);
        this.html_input.html(blog.html);
        this.title_input.val(blog.title);
        this.cate_input.val(blog.category);
        this.tags_input.val(blog.tags.join(';'));
        this.blog_id=blog.id;
        this.display();
    }
    display(){
        location.href=this.selector;
    }
    submit(){
        var json=this.prepareInfo();
        if(json){
            if(this.mode=='alter'){json.opr_type='alter';json.id=this.blog_id;}
            else {json.opr_type='create';json.id=null;}
            var re=$.post({url:this.submit_url,async:false,data:JSON.stringify(json)}).responseJSON;
            var msg=re.message;
            showMsg(this.msg_box,msg);
            if(re.success)location.reload();
        }
    }
    prepareInfo(){
        var title=this.title_input.val();
        var cate=this.cate_input.val();
        var tags=this.tags_input.val().split(';');
        var md=this.text_input.val();
        if(title.trim()==''){showMsg(this.msg_box,'标题不能为空！');return false;}
        if(cate.trim()==''){showMsg(this.msg_box,'目录不能为空！');return false;}
        if(md.trim()==''){showMsg(this.msg_box,'文章不能为空');return false;}
        var json={title:title,category:cate,tags:tags,md:md};
        return json;
    }

}


function initEditableSwitch(){
    var edit_toobar=$('#edit-toolbar');
    var btn=$('.switch-editable');
    var btn_ilz=new SwitchInitializer(btn);
    var tar1=btn_ilz.tar1;var tar2=btn_ilz.tar2;
    var sw=new Switch(btn,()=>{
        tar1.attr('contenteditable','true');
    },
    ()=>{
        tar1.attr('contenteditable','false');
        var sw_dv=switches.doubleview[0];
        sw_dv.easyTurnOff();
    });
    switches['editable']=[];
    switches.editable.push(sw);
}
//-----------------insert blog and edit-----------//

//----------------cmd---------------//

function initCommandButton(){
    var btn=$('.cmd-btn');
    var input=$('.cmd-input');
    var msg_box=$('.msg-box-tem');
    var funcs={
        "edit":()=>{
            var sw=switches.editable[0];
            var btn=$('#btn-editable');
            show(btn);
            sw.easyTurnOn();
            return true;
        },
        "exit":()=>{
            var sw=switches.editable[0];
            sw.easyTurnOff();
            return true;
        },
        "mode":(param)=>{
            if(param=='close'){
                fman.closeMode();
                return true;
            }
            else if(param=='dark'){
                fman.setMode('mode-dark');
            return true;
            }
            return false;
        },
        "#":(param)=>{
            location.href="#" + param;
        }
    }
    new Commander(input,btn,funcs,msg_box);
}
//--------------gather blog info-----------------//

//----------end cmd-----------//
function initSwitchTest(){
    initEditableSwitch();
    initCommandButton();
    initSwitch();
}
function initEditor(){
    editor_app=new Editor('#editor');
    fman=new FaceManager('#editor');
    var app=editor_app;
    var b=$('body');
    var chg=$('#changeable');
    var sub=$('#submit-btn');
    var text_input=$('#text-input');
    var html_input=$('#html-input');
    var sw=$('#exitview-switch');
    var msg_box=$('.msg-box-tem');
    initSwitchTest();
    initMarked();
    copyText(text_input,html_input);
    text_input.unbind().on("propertychange focus input",()=>{
        copyText(text_input,html_input);
    });
    html_input.unbind().on("propertychange focus input",()=>{
        copyHtml(html_input,text_input);
    });
    sub.click((e)=>{
        editor_app.submit();
    });

}
$(document).ready(()=>{
    initEditor();
})