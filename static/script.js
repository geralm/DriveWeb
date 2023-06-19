$(document).ready(function () {
    $('#productosEnPostsBtn').click(function () {
        var productsDictionary = $('#productsDictionary').val();
        $.ajax({
            url: '/home/ShowList',
            method: 'POST',
            data: { productsDictionary: productsDictionary },
            success: function (response) {
                window.location.href = '/home/products?result=' + response;
            },
            error: function (error) {
                // Manejar el error si es necesario
            }
        });
    });
});
