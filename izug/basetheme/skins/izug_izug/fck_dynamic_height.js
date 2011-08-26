
jq(function(){
    var isIE6 = jq.browser.version=="6.0";
    if(isIE6==false){
        var resiableAreas = jq('[id$="_fckContainer"]');
        var iframe = jq('[id$="___Frame"]',resiableAreas);
        var fwidth = iframe.attr('width');
        iframe.attr('height','100%');    
        resiableAreas.resizable({maxWidth:fwidth,minWidth:fwidth, minHeight:200, maxHeight:900,handles:'s,se',helper: 'ui-state-highlight'});
        resiableAreas.parent().css('width',fwidth+'px');
    }
});
