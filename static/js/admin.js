$(document).ready(function () {
  $('select').material_select();
  $('.modal-trigger').leanModal();

  $('i.deleteAdmin').click(function (ev) {
    ev.preventDefault();
    ev.stopPropagation();
    $(this).parents('.chip').fadeOut('slow');
    var admin = $(this).parents('.chip').find('.id').text().trim();
    $.post('/admin/delete_admin', {admin: admin}, function () {
      window.location.reload();
    });
    return false;
  });
});
