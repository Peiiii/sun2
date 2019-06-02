
function getScreenSize(){
    var width=(visualViewport || screen).width;
    var body=$('body');
    body.removeClass('screen-xs screen-md');
    if(width<770)body.addClass('screen-xs');
    else body.addClass('screen-md');
}
function initManage(){
    getScreenSize();
    $(window).on('resize',()=>{getScreenSize();})
}
$(document).ready(()=>{
    initManage();
})