

function checkResp(jr,ctl_id){
    blog_box=$('#blog_box_'+ctl_id)
    msg_box=$('#msg_box_'+ctl_id);
    msg_show=$('#msg_show_'+ctl_id)[0];
    known_btn=$('#known_btn_'+ctl_id);
    msg_show.innerHTML=jr['message'];
    msg_box.css('display','block');
    known_btn.click(function (){
        blog_box.remove();
    });
    return jr['success'];
}
function delete_blog(blog_id,ctl_id){
    $.get('/user/manage/api_delete_blog/'+blog_id,function(jr){
        suc=checkResp(jr,ctl_id);
    })
}

