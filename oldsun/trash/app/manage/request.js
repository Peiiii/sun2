
function getBlog(id){
    var text_input=$('#text-input');
    var json={blog_id:id};
    var re=$.post({url:'/manage/get_blog',async:false,data:JSON.stringify(json)}).responseJSON;log(re)
    if(re.success){
       return re.data;
    }
    return false;
}
