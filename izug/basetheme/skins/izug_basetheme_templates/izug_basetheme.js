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
    jQuery(function($){
        $('.portalMessage dd').append(
            '<span class="messageClose function-delete">&nbsp;</span>').find(
                '.messageClose').click(function(e){
                    $(this).parents('.portalMessage:first').fadeOut(
                        200, function() {$(this).remove();});
                });
    });

    /* extjs loads a blank image from extjs.com - we want to prevent that */
    jQuery(function($){
        if (window.Ext != undefined) {
            Ext.BLANK_IMAGE_URL= $("#portal-logo").attr('href') + "/s.gif";
        }
    });

    /* zug collapsible */
    jq('dl.zugCollapsible dd').hide();
    jq('dl.zugCollapsible dt').prepend('<span class="function-collapsible-closed">&nbsp;</span>');
    jq('dl.zugCollapsible dt').click(function() {
        jq(this).find('span').toggleClass('function-collapsible-closed').toggleClass('function-collapsible-open');
        var content = jq(this).next('dd');
        content.toggleClass('visible');
        if(content.hasClass('visible')) {
            content.slideDown('slow');
        } else {
            content.slideUp('slow');
        }

    });
    jq('dl.zugCollapsible dt a').click(function(e) {
         e.stopPropagation();
    });
});
