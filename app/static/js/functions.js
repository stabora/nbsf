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
					'./consultarPadron?entorno=TESTING&numeroDocumento=' + $(this).val(),
					function(data)
					{
						nombre = $(data).find('Nombre1').text()

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

	$('form[name=alta-baja-prestamos]')
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
			uidPrestamo: {
					validators: {
							callback: {
									message: 'Ingrese un valor',
									callback: function(value, validator, $field)
									{
											var accion = $('form[name=alta-baja-prestamos] input[name=accion]:checked').val();
											return (accion !== 'AltaEnWF') ? true : (value !== '');
									}
							}
					}
			}
		}
	})
	.on('success.form.bv', function(e, data)
	{
		if (
			$('form[name=alta-baja-prestamos] input[name=accion]:checked').val() == 'BajaEnWF'
			&& ! $('form[name=alta-baja-prestamos] input[name=uidPrestamo]').val()
		) {
			mostrarConfirmacionModal('Se solicitará la baja de todos los préstamos pendientes para el cliente', 'alert-danger')
			$('#confirmacionOK').click(function() { $('form[name=alta-baja-prestamos]')[0].submit() });

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


	// Formulario consulta legajo digital

	$('form[name=consulta-legajo-digital]')
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

	$('form[name=consulta-legajo-digital] input[name=numeroDocumento], form[name=consulta-legajo-digital] select[name=tipoDocumento]').change(function()
	{
		$('form[name=consulta-legajo-digital] input[name=numeroCliente]').val(
			generarNITCliente(
				$('form[name=consulta-legajo-digital] select[name=tipoDocumento]').val(),
				$('form[name=consulta-legajo-digital] input[name=numeroDocumento]').val()
			));
	});


	// Legajo digital - Selección de documentos

	if($('div#legajoDigitalSeleccion').length)
	{
		$('input[type="radio"][value="D"]').click(function()
		{
			if($('input[rel="' + $(this).attr('name') + '"]').not(':checked').size() == 0)
			{
				return true;
			} else {
				mostrarAvisoModal('Debe revisar la versión digital para poder seleccionarla.', 'alert-danger');
				return false;
			}
		});


		$('.image-preview, .document-preview').click(function()
		{
			if($(this).attr('rel'))
			{
				$(document).find('input[name="chk-' + $(this).attr('rel') + '"]').attr('checked', 'true');
				$(this).css('opacity', '0.5');
			}
		});


		$('.verificar-seleccion').click(function()
		{
			if($('input[type="radio"]:checked').size() == $('input[type="radio"]').size() / 2)
			{
				mostrarAvisoModal('Documentación seleccionada.\n', 'alert-success');
			} else {
				mostrarAvisoModal('Debe seleccionar toda la documentación.', 'alert-danger');
			}
		});
	}


	// Inicialización de elementos tooltip

	$('a[data-toggle="tooltip"]').tooltip();


	// Inicialización de confirmación modal

	$('a[data-confirm]').click(function(ev)
	{
		mostrarConfirmacionModal($(this).attr('data-confirm'), 'alert-danger');
		$('#confirmacionOK').attr('href', $(this).attr('href'));

		return false;
	});


	// Foco en el primer campo del formulario activo

	$("form input:text, form textarea").first().focus();


	// Image preview

	$('.image-preview').on('click', function()
	{
		$('#image-preview').attr('src', $(this).find('img').attr('src').replace('FileMiniature', 'File'));
		$('#image-preview-title').html($(this).find('img').attr('title'));
		$('#image-preview-link').attr('href', $(this).find('img').attr('src').replace('FileMiniature', 'File'));
		$('#image-preview-modal').modal('show');
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

function generarConfirmacionModal(texto, estilo, titulo)
{
	if( ! $('#confirmacionModal').length)
	{
		if(typeof titulo === "undefined")
		{
			titulo = 'Confirmar acci&oacute;n';
		}

		if(typeof estilo === "undefined")
		{
			estilo = '';
		}

		$('body').append(
			'<div id="confirmacionModal" class="modal fade" role="dialog" aria-labelledby="confirmacionModalLabel" aria-hidden="true" tabindex="-1">' +
			'<div class="modal-dialog">' +
			'<div class="modal-content ' + estilo + '">' +
			'<div class="modal-header">' +
			'<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>' +
			'<h3 id="confirmacionModalLabel">' + titulo + '</h3>' +
			'</div>' +
			'<div class="modal-body">' + texto + '</div>' +
			'<div class="modal-footer">' +
			'<button class="btn" data-dismiss="modal" aria-hidden="true">Cancelar</button>' +
			'<a class="btn btn-danger btn-ok" id="confirmacionOK">Continuar</a>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'</div>'
		);
	}
}

function mostrarConfirmacionModal(texto, estilo, titulo)
{
	$('#confirmacionModal').remove();
	generarConfirmacionModal(texto, estilo, titulo);
	$('#confirmacionModal').modal({ show: true });
	$('button[type="submit"]').prop('disabled', false);
}


function generarAvisoModal(texto, estilo, titulo)
{
	if( ! $('#avisoModal').length)
	{
		if(typeof titulo === "undefined")
		{
			titulo = 'Aviso';
		}

		if(typeof estilo === "undefined")
		{
			estilo = '';
		}

		$('body').append(
			'<div id="avisoModal" class="modal fade" role="dialog" aria-labelledby="avisoModalLabel" aria-hidden="true">' +
			'<div class="modal-dialog">' +
			'<div class="modal-content ' + estilo + '">' +
			'<div class="modal-header">' +
			'<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>' +
			'<h3 id="avisoModalLabel">' + titulo + '</h3>' +
			'</div>' +
			'<div class="modal-body">' + texto + '</div>' +
			'<div class="modal-footer">' +
			'<button class="btn btn-primary" data-dismiss="modal" aria-hidden="true">Aceptar</button>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'</div>'
		);
	}
}

function mostrarAvisoModal(texto, estilo, titulo)
{
	$('#avisoModal').remove();
	generarAvisoModal(texto, estilo, titulo);
	$('#avisoModal').modal({ show: true });
}
