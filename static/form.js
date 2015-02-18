$(document).ready( function() {
    $('#add_entry').submit( function(event) {
        event.preventDefault();
        var title = $('input[name=title]').val();
        var text = $('textarea#text').val();
        $.ajax({
            url : "add",
            type : "POST",
            dataType : "json",
            data : { 
            'title' : title, 
            'text' : text },
        }).done(function(data) {
            alert("title = " + data.title);
        })
    });
});
