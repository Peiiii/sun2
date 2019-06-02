
var home={};
function initScreen(){
    var width=screen.width;
    var body=$('body');
    if(width<=500)body.addClass('screen-sm');
}
function switch_fold_on(tar){
    tar.addClass('blog-mask');
}
function switch_fold_off(tar){
    tar.removeClass('blog-mask');
}

class SwitchFold extends Switch{
    constructor(btn,tar){
        super(btn,()=>{switch_fold_on(tar);},()=>{switch_fold_off(tar)});
    }
}
function initBlog(blog){
    var mask=blog.find('.wrapper1');
    var unfold=blog.find('.switch-fold');
    if(mask.height()>300){new SwitchFold(unfold,mask);show(unfold);}
    else{hide(unfold);}

}
function initHome(){
    home.blogs=$('.blog');
    home.blogs.map((n,blog)=>{
        var blog=$(blog);
        initBlog(blog);
    })

}
$(document).ready(()=>{
    initHome();
})