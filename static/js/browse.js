$(document).ready(function () {
    $('select').material_select();

    $('li.disabled').click(function () {
      event.preventDefault();
      return false;
    });

    $('#pageSizeSelector').change(function () {
      window.location.href = '/browse' + '?page_size=' + $('#pageSizeSelector').val();
    });
});
