$(function () {
    $('#close-checkin').click(function () {
        $.ajax({
            url: '/close_checkin',
            type: 'POST',
            success: function (response) {
                $('#check-in-message').text(response.message);
            }
        });
    });
});