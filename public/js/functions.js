$(document).ready(function()
{
	form = $('form[name=consulta-veraz]')
	.bootstrapValidator(
	{
		feedbackIcons:
		{
			valid: 'glyphicon glyphicon-ok',
			invalid: 'glyphicon glyphicon-remove',
			validating: 'glyphicon glyphicon-refresh'
		},

		fields:
		{
			numeroDocumento: { validators: { integer: { message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } },
			nombre: { validators: { notEmpty: { message: 'Ingrese un valor' } } },
			sexo: { validators: { notEmpty: { message: 'Seleccione una opción' } } }
		}
	});

	form.on('success.field.bv', function(e, data) {
		data.bv.disableSubmitButtons(false);
	});

	form.on('success.form.bv', function(e, data) {
		$('button[name=consultar]').toggleClass('active');
	});


	$('input[name=numeroDocumento]')
		.focus()
		.blur(function()
		{
			if($(this).val())
			{
				$.get(
					'/nbsf/consultaPadron?numeroDocumento=' + $(this).val(),
					function(data)
					{
						nombre = $(data).find('Nombre1').text().replace(' ', ', ')

						if(nombre)
						{
							$('input[name=nombre]').val(nombre);
						}

						sexo = $(data).find('Sexo1').text();

						if(sexo)
						{
							$('input:radio[name=sexo][value=' + sexo + ']').prop('checked', true)
						}
					});

				form.data('bootstrapValidator').resetForm();
			}
		});
});