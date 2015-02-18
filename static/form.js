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
            var title =  $('<h3></h3>').text(data.title);
            var date = $('<p>').addClass("dateline").text(data.created);
            var text = $('<div></div>').addClass("entry_body").html(data.text);
            var link_button = $('<a></a>').attr('href', 'detail/' + data.id);
            link_button.append($('<button></button>').attr("type", "button").text("permalink"));
            var edit_button = $('<a></a>').attr('href', 'edit/' + data.id);
            edit_button.append($('<button></button>').attr("type", "button").text("edit"));
            id.append(title, date, text, link_button, edit_button);
            $('#entries').prepend(id);
        })
    });
});

// <article class="entry" id="entry={{entry.id}}">
//       <h3>{{ entry.title }}</h3>
//       <p class="dateline">{{ entry.created.strftime('%b. %d, %Y') }}
//       <div class="entry_body">
//         {{ entry.text|markdown|safe }}
//       </div>
//       <a href ="{{request.route_url('detail', id=entry.id)}}">
//         <button type="button">permalink</button>
//       </a>
//       {% if request.authenticated_userid %}
//         <a href ="{{request.route_url('edit', id=entry.id)}}">
//           <button type="button">edit</button>
//         </a>
//       {% endif %}
//     </article>
