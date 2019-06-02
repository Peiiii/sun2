//base : jsquery,boostrap(only show and hide)
dev=true;
hi='hi';
hi1='hi1';
hi2='hi2';
hi3='hi3';
var trash={app:{},modules:['base']}
function show(el){
    el.removeClass('hidden');
}
function hide(el){
    el.addClass('hidden');
}
function hide_or_show(el){
    if(el.hasClass('hidden'))show(el);
    else hide(el);
}
String.prototype.replaceAll = function(s1,s2){
return this.replace(new RegExp(s1,"gm"),s2);
}
String.prototype.escape2text=function(){
    var ret= this.replaceAll('<div>','').replaceAll('</div>','\n').replaceAll('<br>','\n');
    console.log(ret)
    return ret;
}
String.prototype.strip=function(str=' '){
 //类似于 python 的 strip 函数
    context=this;
    len=str.length;
//    log(context);log(len)
    if(context.length<len)return context;
    while(true){
        if(context.length<len) return context;
        s1=context.slice(0,len);
        if(s1===str)context=context.slice(len,);
        else break;
    }
    while(true){
        if(context.length<len) return context;
        s2=context.slice(-len,);
        if(s2===str)context=context.slice(0,-len);
        else break;
    }
    return context;
}
String.prototype.mul=function(num){
    var str=''
    for(var i=0;i<num;i++){
        str+=this;
    };
    return str;
}
String.prototype.toDict= function(divider=';'){
//类似于对cookies的解析函数，将纯字符串的键=值对集合解析成集合，divider为分隔符。
//例如 对 "name=nick&&key=123&&code=345" 进行解析，divider="&&",返回结果 { name:nick',key:'123',code:'345'}
    var text=this.strip(divider);
    var arr=text.split(divider);
    var dic={};
    for(var i=0;i<arr.length;i++){
        [name,value]=arr[i].split('=');
        dic[name]=value;
    }
    return dic;
}
String.prototype.getRows=function (t){
//计算字符串中换行符数量
    arr=t.split('\n')
    return arr.length;
}
function getLastLine(text){
    text=text.split('\n');
    return text[text.length-1];
}
function getFirstLine(text){
    text=text.split('\n');
    return text[0];
}
function getLine(text,n){
    num=0;
    for(var i=0;i<n;i++){
        if(text[i]=='\n')num++;
    };
    line =text.split('\n')[num];
    //log(line);
    return line;
}
function getHeadAndBody(text,from_start=true){
    text=text.trim();
    var pat=new RegExp('^\\/\\*[\\s\\S]*\\*\\/');
    var m=text.match(pat);
    if(!m)return [null,text];
    var body=text.replace(pat,'');
    var head=m[0];
    return [head,body];
}
//----------------------------------------------//
// document format conversion
function escapeToHTML(str) {
 var arrEntities={'lt':'<','gt':'>','nbsp':' ','amp':'&','quot':'"'};
 return str.replace(/&(lt|gt|nbsp|amp|quot);/ig,function(all,t){return arrEntities[t];});
}

//-------------------------------------------------------//
Array.prototype.wash=function(){
    var new_arr=[]
    for(var i=0;i<this.length;i++ ){
        var s=this[i].trim();
        if(s)new_arr.push(s);
    }
    return new_arr;
}

//------------------------------------------------//
//常用函数
function log(text){console.log(text);}
function slog(text,str='',num=10){
    console.log('*'.mul(num));
    console.log(text);
    console.log('*'.mul(num));
}
function flag(text){
    slog('Hi,this is a flag. '+text);
}