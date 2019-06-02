function alterEditBlog(id){
    var blog=getBlog(id);
    if(blog)editor_app.editBlog(blog);
}
function deleteBlog(id){
    var msg_box=$('.msg-box-tem');
    var title=$('#'+id).find('.blog-title').text();
    var msg=`Are you sure to delete <code>${title}</code> <button onclick="deleteBlog2('${id}')">I'm Sure</button>`;
    showMsg(msg_box,msg);
}
function deleteBlog2(id){
    var msg_box=$('.msg-box-tem');
    var json={
        id:id,opr_type:'delete'
    }
    var re=$.post({url:'/manage/alter',async:false,data:JSON.stringify(json)}).responseJSON;
    log(re)
    if(re.success){location.reload();log('success')}
    else showMsg(msg_box,re.message);
}
$(document).ready(()=>{

})