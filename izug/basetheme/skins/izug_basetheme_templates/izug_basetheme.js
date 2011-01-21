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
    jq("dl.info").delay(5000).fadeOut("slow");
});
