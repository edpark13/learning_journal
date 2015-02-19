$(document).ready( function() {    
    $('#edit_form').hide(); // form off
    var id = $('article[class=single_entry]').attr("id");
    event.preventDefault();
    $.ajax({
        url : "../edit",
        type : "GET",
        dataType : "json",
        data : { 
        'id' : id},
    }).done(make_form);

    $('#edit').click( function(event) {
        $('#edit_form').toggle(); // form ON
        $('#entry').toggle(); // entry OFF
    });

    function make_form(data) {
        $('input[name=title]').attr("value", data.title);
        $('textarea#text').text(data.text);
    }

    $('.edit_entry').submit( function(event) {
        event.preventDefault();
        // alert('in function')
        var title = $('input[name=title]').val();
        var text = $('textarea#text').val();
        var id = $('article[class=single_entry]').attr("id");
        $.ajax({
            url : "../edit",
            type : "POST",
            dataType : "json",
            data : { 
            'title' : title, 
            'text' : text,
            'id' : id },
        }).done(function(data) {
            $('<h3></h3>').text(data.title);
            $('.entry_body').html(data.text);
            $('#edit_form').toggle(); // form OFF
            $('#entry').toggle(); // entry ON
        });
    });
});

