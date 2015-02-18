$(document).ready( function() {
    $('#submit').click( function() {
        event.preventDefault();
        var title = $('input[name=title]').val();
        var text = $('textarea#text').val();
        // alert(title + " and " + text);
        // var request = $.post( "add", function() {
        //     alert( "success" );
        // })
        $.ajax({
            url: "add",
            type : "POST",
            data : { 
            'title' : title, 
            'text' : text },
        }).done(function( data ) {
        alert(data)
    });
  });
    //     }).done(get_entries(text))
    //     // .done(function( msg ) {
    //     //     alert( "Data Saved: " + msg );
    //     // });
    // });
    // function get_entries(text) {
    //     // alert("works!")
    //     var entries = $.ajax({
    //         url : "home",
    //         type : "GET",
    //     }).done(function(msg) {
    //         alert(msg);
    //     });
    //     // get_entry(entries, text)
    // }
});
