$(document).ready(function () {
    $('select').material_select();

    $('li.disabled').click(function () {
      event.preventDefault();
      return false;
    });

    $('#pageSizeSelector').change(function () {
      var params = $(this).data('params');
      var inputs = $('input').serialize();
      window.location.href = '/browse' + '?page_size=' + $('#pageSizeSelector').val() + '&' + inputs + '&' + params;
    });

    $('#searchText').keyup(function (event) {
      if(event.keyCode == 13) {
        var params = $(this).data('params');
        var inputs = $('input').serialize();
        window.location.href = '/browse' + '?page_size=' + $('#pageSizeSelector').val() + '&' + inputs + '&' + params;
      }
    });

    $('a.clearFilter').click(function () {
      $('select option', $(this).closest('div.row')).removeAttr('selected');
      $('select').material_select();
    });

    $('select[name=sort_order]').change(function () {
      $('div#filters form').submit();
    });

    $('div#filters form').submit(function () {
      if(!$('select[name=years]').val()) {
        $('form input[name=years_cleared]').val('1');
      }
      if(!$('select[name=schools]').val()) {
        $('form input[name=schools_cleared]').val('1');
      }
    });
});
