//cimport('file');
config=new Object();
config.default_path='./static';
config.msg_box=$('.msg-box');
function postfs(json){
    var re=$.post({url:'/manage/fs',data:JSON.stringify(json),async:false}).responseJSON;
    if(re.success){
        return re.data;
    }
    else {
        showMsg(config.msg_box,re.message);
    }
}
function mkdir(path){
    var json={
        optype:'mkdir',
        path:path
    }
    return postfs(json);
}
function mkfile(path){
    var json={
        optype:'mkfile',
        path:path
    }
    return postfs(json);
}
function remove(path){
    //remove file
    var json={optype:'remove',path:path};
    return postfs(json)
}
function rename(src,dst){
    //remove file
    var json={optype:'rename',src:src,dst:dst};
    return postfs(json)
}
function rmdir(path){
    //remove file
    var json={optype:'rmdir',path:path};
    return postfs(json)
}
function getDir(path){
    var json={
        optype:'getdirinfo',
        path:path
    }
   return postfs(json);
}
function runFileExplorer(){
    var default_path=config.default_path;
    var dir=getDir(default_path);
     fe=new Vue({
        delimiters:['<%','%>'],
        el:'#file_explorer',
        data:{
            path:dir,
            path_history:[default_path],
            his_length:1
        },
        methods:{
            pathForward:function(e){
//                log(e);
                var path=e.target.getAttribute('path');
                var p=getDir(path);
//                log(p);
                this.$data.path=p;
                log(this.$data.path.name)
//                var len=this.$data.his_length;
                this.$data.path_history.push(path);
                this.$data.his_length++;
            },
            pathBackward:function(e){
//                log(e);
                if(this.$data.his_length==1)return false;
                this.$data.path_history.pop();
                this.$data.his_length--;
                var path=this.$data.path_history.slice(-1)[0];
                //log(path)
                var dir=getDir(path);
                this.$data.path=dir;
            },
            toPathTop:function(e){
                var path=this.$data.path_history[0];
                var dir=getDir(path);
                this.$data.path_history.push(path);
                this.$data.his_length++;
                this.$data.path=dir;
            },
            update:function(){
                var path=this.$data.path.path;
                this.$data.path_history.pop();this.$data.his_length--;
                var dir=getDir(path);
                this.$data.path=dir;
                this.$data.path_history.push(dir);
                this.$data.his_length++;
                log(this.$data.path)
            },
            createNewDir:function(e){
                mkdir(this.$data.path.path+'/'+'untitled');
                this.update();
            },
            createNewFile:function(e){
                mkfile(this.$data.path.path+'/'+'untitled.txt');
                this.update();
            },
            execute:function(e){
                var el=$(e.target);
                var optype=el.attr('optype');
                var path=el.attr('path');
                if(optype=='rmdir'){
                    rmdir(path);
                    this.update();
                }
                else if(optype=='remove'){
                    remove(path)
                    this.update();
                }
                else if(optype=='rename'){
                    var head=el.attr('head');
                    var oldpath=$(head).attr('path');
                    head=$(head).find('.path-name');
                    head.attr('contenteditable','true');
                    var s=window.getSelection();
                    var self=this;
                    head.focusout(()=>{
                        var newname=head.text();
                        var dst=self.$data.path.path+'/'+newname;
                        rename(oldpath,dst);
                        head.attr('contenteditable','false');
                        head.unbind('focusout');
                        self.update();
                    })
//                    select(head);
                }
            }
        },
        created:function(){
        }
    })
}

$(document).ready(function(){
    runFileExplorer();
})