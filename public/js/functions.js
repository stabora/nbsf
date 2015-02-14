$(document).ready(function()
{

	// Formulario consulta Veraz

	$('form[name=consulta-veraz]')
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
		})
		.on('success.field.bv', function(e, data)
		{
			data.bv.disableSubmitButtons(false);
		})
		.on('success.form.bv', function(e, data)
		{
			$('button[name=consultar]').toggleClass('active');
		});


	$('form[name=consulta-veraz] input[name=numeroDocumento]')
		.focus()
		.blur(function()
		{
			if($(this).val())
			{
				$.get(
					'/nbsf/consultarPadron?numeroDocumento=' + $(this).val(),
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


	// Formulario consulta CUAD

	$('form[name=consulta-cupo-cuad]')
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
			numeroCuit: { validators: { regexp: { regexp: /[0-9]{11}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[name=consultar]').toggleClass('active');
	});

	$('form[name=consulta-cupo-cuad] input[name=numeroCuit]').focus();


	// Formulario consulta datos cliente

	$('form[name=consulta-cliente]')
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
			numeroCliente: { validators: { regexp: { regexp: /[0-9]{12,13}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[name=consultar]').toggleClass('active');
	});

	$('form[name=consulta-cliente] input[name=numeroCliente]').focus();

});
