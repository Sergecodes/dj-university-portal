
/** This file MUST be used alongside the core/bookmarking.html template */
// some variables used here are defined in the bookmarking.html file.

$('.js-bookmark-button').click(function(event) {
    // if user isn't logged in
    if (!userId) {
        displayLoginRequiredToast();
        return false;
    }

    var $this = $(this);
    var $icon = $this.children('i'), id = parseInt(this.dataset.id, 10);
    
    // if user is trying to undo the bookmark
    if ($icon.hasClass('js-selected')) {
        var voteAction = 'recall-bookmark';

        $.ajax({
            url: bookmarkUrl,
            type: 'POST',
            data: {id: id, action: voteAction},
            dataType: 'json',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(result) {
                if (result['unbookmarked']) {
                    // remove fas(font-awesome solid) class and set to far(font-awesome regular)
                    $icon.removeClass('fas js-selected').addClass('far');

                    // update bookmark count
                    var newCount = parseInt($bookmarkCounter.text(), 10);
                    $bookmarkCounter.text(newCount - 1);

                    // update text
                    var textNode = $icon[0].nextSibling;
                    textNode.textContent = " " + bookmarkText;
                    displayBookmarkToggleToast(false);

                } else {
                    console.error(result);
                    displayErrorOccurredToast();
                }
            }
        });

    } else {
        // if user is adding a new bookmark
        var voteAction = 'bookmark';

        $.ajax({
            url: bookmarkUrl,
            type: 'POST',
            data: {id: id, action: voteAction},
            dataType: 'json',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(result) {
                if (result['bookmarked']) {
                    // remove far class and set to fas
                    $icon.removeClass('far').addClass('fas js-selected');

                    // update bookmark count
                    var newCount = parseInt($bookmarkCounter.text(), 10);
                    $bookmarkCounter.text(newCount + 1);

                    var textNode = $icon[0].nextSibling;
                    textNode.textContent = " " + bookmarkedText;
                    displayBookmarkToggleToast(true);
                } else {
                    console.error(result);
                    displayErrorOccurredToast();
                }
            }
        });
    }
});