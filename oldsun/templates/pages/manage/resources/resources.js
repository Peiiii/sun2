
//$("#file-input").fileinput();
$("#file-input").fileinput({'showUpload':false, 'previewFileType':'any','uploadUrl':'/manage/fs',
    uploadExtraData:{optype:'upload'}
});
function postFile(file){
//    $.post({url:'/manage/fs',data='json'})
}
function initFileUpload(){
    var res=$('#resources');
    var file_input=$('#file_input');
    var btn_sub=res.find('button[type=submit]');
    btn_sub.submit(()=>{
        var file=file_input[0].files[0];
        var json={};
    })

}
function initResources(){

    var fs_view=$('.fs_view');
    var dir={children:[]};
    var vue = new Vue({
        el: '#resources',
        delimiters:['<%','%>'],
        data: {
            dir:dir
        }
    })

    var json={
        optype:'getdirinfo',
        path:'e:/sun/www/static'
    }

    var re=$.post({url:'/manage/fs',async:false,data:JSON.stringify(json),success:(resp)=>{
//        console.log(resp);
        vue.$data.dir=resp.data;
    }}).responseJSON;
    if(re.success)var dir=re.data;
    else{log('failed');return}
}


$(document).ready(()=>{
    initResources();
})

