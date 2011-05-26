jq(document).ready(function() {
    /*var legends = jq("#content fieldset>legend");
    legends.prepend("<div class='collapsibleLegend'");
    // attach a live event to the newly added handler
    jq('.collapsibleLegend').bind('click', function() {
        if (jq(this).hasClass("closed")) {
            jq(this).closest("fieldset").children().not("legend").slideDown("slow");
            jq(this).toggleClass("closed");
        } else {
            jq(this).closest("fieldset").children().not("legend").slideUp("slow");
            jq(this).toggleClass("closed");
        }
    });*/
    
    /* fading out info messages as defined in Design_Fundamentals_1_0_v7.pdf, page 24 */
    setTimeout("jq('dl.info').fadeOut('slow')", 5000);
    
    /* extjs loads a blank image from extjs.com - we want to prevent that */
    if (window.Ext != undefined) {
        Ext.BLANK_IMAGE_URL= jq("#portal-logo").url() + "/s.gif";
    }
});
