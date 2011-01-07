jq(document).ready(function() {
    var legends = jq("#content fieldset>legend");
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
    });
});
