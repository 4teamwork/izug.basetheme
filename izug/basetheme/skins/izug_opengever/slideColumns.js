jq(document).ready(function() {
    var columnWrapper = jq("#portal-columns");
	var columnOne = jq("#portal-column-one");
    var columnContent = jq("#portal-column-content");

    function setColumnOneWidth(width) {
    	var contentWrapperWidth = columnWrapper.width();
    	var contentWidth = contentWrapperWidth-width;
        columnContent.css("width", contentWidth+"px");
        columnContent.css("margin-left", "-" + contentWidth +"px");
        columnOne.css("width", width+"px");
        columnOne.css("left", contentWrapperWidth+"px");
    }
    if (columnOne) {
        columnOne.resizable({ 
	      handles: 'e',
          ghost: true,
          minWidth: 200,
          maxWidth: 500,
          resize: function(event, ui) {
	          setColumnOneWidth(ui.size.width);
          },
          stop: function(event, ui) {
              jq.get("setColumnsWidth?left="+ui.size.width+"px&content="+columnContent.width()+"px");
              //jq("#state").load("setColumnsWidth?left="+ui.size.width+"px&content="+columnContent.width()+"px");
          }
	    });
	    jq(window).resize( function() { 
	    	setColumnOneWidth(columnOne.width());
	    });
	}
});