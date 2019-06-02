
class WordQuerier{
    constructor(base_url='http://www.iciba.com'){
        this.base_url=base_url;
    }
    get(url){}
    joinPath(latter){return this.base_url+'/'+latter;}
    query(word){
        var url=this.joinPath(word);
        var re=$.post({url:'/proxy/get',data:JSON.stringify({url:url}),async:false});
        return this.parse(re.responseText);
    }
    parse(html){
       var doc=$(html);
       var s1=doc.find('.container-left').find('.js-base-info').find('.in-base');
       var item1=s1.find('.in-base-top').html()
       var item2=s1.find('.base-list').html()
       var item3=s1.find('.change').html();
       var html='';
       if(item1)html+=item1;
       if(item2)html+=item2;
       if(item3)html+=item3;
       return html;
    }
}

flag('query opend');
querier=new WordQuerier();
$(document).ready(()=>{
    var blogs=$('.blog');
    var msg_box=$('.msg-box');
//    var test_div=$('.test-msg-box');
    if(smartphone)return slog('smartphone : not execute this.');
    blogs.map((n,b)=>{
        b=$(b);
        b.click(()=>{
//            test_div.html('clicked');
            var text=window.getSelection().toString();
//            test_div.html('text selected:'+text);
            if(text.trim()=='')return hideMsg(msg_box);
//            test_div.html('text selected:'+text);
            slog(text);
            var text=querier.query(text);
            showMsg(msg_box,text);
//            test_div.html(text);
        })
    })
})



