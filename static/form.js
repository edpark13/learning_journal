!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');
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
            var id = $('<article></article>').attr({
                "class" : "entry",
                "id" : data.id
            });
            var twitter = '<a href="https://twitter.com/share" class="twitter-share-button" data-text='+ data.title +' data-via="edpark13" data-size="large" data-count="none">Tweet</a>'
            var title =  $('<h3></h3>').text(data.title);
            var date = $('<p>').addClass("dateline").text(data.created);
            var text = $('<div></div>').addClass("entry_body").html(data.text);
            var link_button = $('<a></a>').attr('href', 'detail/' + data.id);
            link_button.append($('<button></button>').attr("type", "button").text("permalink"));
            var edit_button = $('<a></a>').attr('href', 'edit/' + data.id);
            edit_button.append($('<button></button>').attr("type", "button").text("edit"));
            id.append(title, date, text, link_button, edit_button, twitter);
            $('#entries').prepend(id);
            twttr.widgets.load();
        })
    });
});
