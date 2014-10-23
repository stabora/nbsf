$(document).ready(function() {
  $('#form-veraz').bootstrapValidator({
      feedbackIcons: {
          valid: 'glyphicon glyphicon-ok',
          invalid: 'glyphicon glyphicon-remove',
          validating: 'glyphicon glyphicon-refresh'
      },
			fields: {
            numeroDocumento: {
                message: 'The username is not valid',
                validators: {
                    notEmpty: {
                        message: 'The username is required and cannot be empty'
                    },
                }
            },
            nombre: {
                message: 'The username is not valid',
                validators: {
                    notEmpty: {
                        message: 'The username is required and cannot be empty'
                    },
                }
            },
        }
  });

	$('input[name=numeroDocumento]')
	.focus()
	.blur(function() {
			if($(this).val()) {
				$.get(
					'/nbsf/consultaPadron?numeroDocumento=' + $(this).val(),
					function(data) {
						$('input[name=nombre]').val($(data).find('Nombre1').text().replace(' ', ', '));
						sexo = $(data).find('Sexo1').text();
						$('input:radio[name=sexo][value=' + sexo + ']').prop('checked', true)
					});
			}
	});
});