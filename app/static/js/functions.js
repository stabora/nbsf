/*------*/
/* Init */
/*------*/

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
				numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } },
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
					'./consultarPadron?numeroDocumento=' + $(this).val(),
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


	// Formulario préstamos pendientes

	$('form[name=consulta-prestamos-pendientes]')
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
			numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});


	// Formulario consulta datos del cliente

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
			numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});

	$('form[name=consulta-cliente] input[name=numeroDocumento], form[name=consulta-cliente] select[name=tipoDocumento]').change(function()
	{
		$('form[name=consulta-cliente] input[name=numeroCliente]').val(
			generarNITCliente(
				$('form[name=consulta-cliente] select[name=tipoDocumento]').val(),
				$('form[name=consulta-cliente] input[name=numeroDocumento]').val()
			));
	});


	// Formulario padrón electoral

	$('form[name=consulta-padron]')
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
			numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
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


	// Formulario bloqueo / desbloqueo de cliente

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
			numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } },
			usuario: { validators: { notEmpty: { message: 'Ingrese un valor' } } },
			operacion: { validators: { notEmpty: { message: 'Seleccione una operación' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});

	$('form[name=desbloqueo-cliente] input[name=numeroDocumento], form[name=desbloqueo-cliente] select[name=tipoDocumento]').change(function()
	{
		$('form[name=desbloqueo-cliente] input[name=numeroCliente]').val(
			generarNITCliente(
				$('form[name=desbloqueo-cliente] select[name=tipoDocumento]').val(),
				$('form[name=desbloqueo-cliente] input[name=numeroDocumento]').val()
			));
	});


	// Formulario baja de préstamos

	$('form[name=baja-prestamos]')
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
			numeroDocumento: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		if( ! $('form[name=baja-prestamos] input[name=uidPrestamo]').val())
		{
			generarDataConfirmModal()

			$('#dataConfirmModal').find('.modal-body').text('Se solicitará la baja de todos los préstamos pendientes para el cliente');
			$('#dataConfirmOK').click(function() { $('form[name=baja-prestamos]')[0].submit() });
			$('#dataConfirmModal').modal({ show: true });
			$('button[type="submit"]').prop('disabled', false);

			return false;
		}

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


	// Formulario consulta SOAT estado tarjeta

	$('form[name=consulta-soat-estado]')
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
			numeroTarjeta: { validators: { regexp: { regexp: /[0-9]{16}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});


	// Formulario consulta API Prieto

	$('form[name=consulta-api-prieto]')
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
			doc: { validators: { regexp: { regexp: /[0-9]{7,12}/, message: 'Número incorrecto' }, notEmpty: { message: 'Ingrese un valor' } } },
			page: { validators: { notEmpty: { message : 'Ingrese un valor' }, greaterThan: { value: 1, message: 'Ingrese un valor mayor a 0' } } },
			limit: { validators: { notEmpty: { message : 'Ingrese un valor' }, between: { min: 1, max: 10, message: 'Ingrese un valor entre 1 y 10' } } }
		}
	})
	.on('success.form.bv', function(e, data)
	{
		$('button[type="submit"]').toggleClass('active');
	});


	// Inicialización de elementos tooltip

	$('[data-toggle="tooltip"]').tooltip();


	// Foco en el primer campo del formulario activo

	$("form input:text, form textarea").first().focus();


	$('a[data-confirm]').click(function(ev) {
		generarDataConfirmModal();

		$('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
		$('#dataConfirmOK').attr('href', $(this).attr('href'));
		$('#dataConfirmModal').modal({ show: true });

		return false;
	});
});


/*---------------------*/
/* Auxiliary functions */
/*---------------------*/

function generarNITCliente(tipoDocumento, numeroDocumento)
{
	if(tipoDocumento && numeroDocumento)
	{
		return tipoDocumento + ('00000000000' + numeroDocumento).slice(-11);
	}
}

function generarDataConfirmModal()
{
	if( ! $('#dataConfirmModal').length)
	{
		$('body').append(
			'<div id="dataConfirmModal" class="modal fade" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true">' +
			'<div class="modal-dialog">' +
			'<div class="modal-content">' +
			'<div class="modal-header">' +
			'<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>' +
			'<h3 id="dataConfirmLabel">Confirmar acci&oacute;n</h3>' +
			'</div>' +
			'<div class="modal-body"></div>' +
			'<div class="modal-footer">' +
			'<button class="btn" data-dismiss="modal" aria-hidden="true">Cancelar</button>' +
			'<a class="btn btn-primary" id="dataConfirmOK">Continuar</a>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'</div>'
		);
	}
}
