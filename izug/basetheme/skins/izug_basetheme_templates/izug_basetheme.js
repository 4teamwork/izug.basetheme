$(document).ready(function() {
    /*var legends = $("#content fieldset>legend");
    legends.prepend("<div class='collapsibleLegend'");
    // attach a live event to the newly added handler
    $('.collapsibleLegend').bind('click', function() {
        if ($(this).hasClass("closed")) {
            $(this).closest("fieldset").children().not("legend").slideDown("slow");
            $(this).toggleClass("closed");
        } else {
            $(this).closest("fieldset").children().not("legend").slideUp("slow");
            $(this).toggleClass("closed");
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
    if (window.Ext != undefined) {
        Ext.BLANK_IMAGE_URL= $("base:first").attr('href') + "s.gif";
    }

    /* zug collapsible */
    $('dl.zugCollapsible dd').hide();
    $('dl.zugCollapsible dt').prepend('<span class="function-collapsible-closed">&nbsp;</span>');
    $('dl.zugCollapsible dt').click(function() {
        $(this).find('span').toggleClass('function-collapsible-closed').toggleClass('function-collapsible-open');
        var content = $(this).next('dd');
        content.toggleClass('visible');
        if(content.hasClass('visible')) {
            content.slideDown('slow');
        } else {
            content.slideUp('slow');
        }

    });
    $('dl.zugCollapsible dt a').click(function(e) {
         e.stopPropagation();
    });
});
