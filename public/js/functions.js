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
			$('button[type="submit"]').toggleClass('active');
		});


	$('form[name=consulta-veraz] input[name=numeroDocumento]')
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

				$('form[name=consulta-veraz]').data('bootstrapValidator').resetForm();
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
		$('button[type="submit"]').toggleClass('active');
	});


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
		$('button[type="submit"]').toggleClass('active');
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
		$('button[type="submit"]').toggleClass('active');
	});


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
		$('button[type="submit"]').toggleClass('active');
	});


	// Formulario desbloqueo de cliente

	$('form[name=desbloqueo-cliente]')
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
			numeroCliente: { validators: { regexp: { regexp: /[0-9]{12,13}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } },
			usuario: { validators: { notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});


	// Formulario consulta cuota máxima mercado abierto

	$('form[name=consulta-cuota-ma]')
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
			uidPrestamo: { validators: { integer: { message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});


	$("form input:text, form textarea").first().focus();
});
