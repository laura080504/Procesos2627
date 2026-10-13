const TEXTOS = {
    es: {
        codigo: "ES",
        login: "Login",
        registro: "Registro",
        email: "Email",
        nick: "Usuario",
        contrasena: "Contraseña",
        recordarme: "Recuerdame",
        olvidaste: "¿Olvidaste la contraseña?",
        recuperar: "Recuperar",
        noRegistrado: "¿No estas registrado aún?",
        creaCuenta: "Crea una cuenta",
        entrar: "Entrar",
        yaTienes: "¿Ya tienes cuenta?",
        iniciaSesion: "Inicia sesión",
        crearCuenta: "Crear cuenta",
        usuarios: "Usuarios",
        gestionUsuarios: "Gestión de usuarios",
        etiquetaRol: "Rol",
        etiquetaEstado: "Estado",
        rolUsuario: "usuario",
        rolAdministrador: "administrador",
        estadoActivo: "activo",
        estadoPendiente: "pendiente",
        estadoEliminado: "eliminado",
        refrescar: "Refrescar",
        cerrarSesion: "Cerrar sesión",
        eliminar: "Eliminar",
        eliminarCuenta: "Eliminar cuenta",
        editar: "Editar",
        editarDatos: "Editar datos",
        editarTitulo: "Editar datos",
        guardarCambios: "Guardar cambios",
        volverGestion: "Volver",
        nuevaContrasenaOpcional: "Nueva contraseña (opcional)",
        datosActualizados: "Datos actualizados",
        hacerAdministrador: "Hacer admin",
        confirmarHacerAdmin: "¿Convertir a {email} en administrador?",
        rolActualizado: "El usuario ahora es administrador",
        cambiarTema: "Cambiar tema",
        cambiarIdioma: "Cambiar idioma",
        dictar: "Dictar",
        verContrasena: "Mostrar contraseña",
        ocultarContrasena: "Ocultar contraseña",
        cuentaCreada: "Cuenta creada. Revisa tu correo y pulsa el enlace para activarla",
        cuentaConfirmada: "Cuenta confirmada. Ya puedes iniciar sesión",
        correoReenviado: "Te hemos vuelto a enviar el correo de confirmación",
        entrarGoogle: "Entrar con Google",
        reenviarConfirmacion: "Reenviar confirmación",
        emailParaReenviar: "Escribe el correo para reenviar la confirmación",
        googleNoConfigurado: "El inicio con Google todavía no está configurado",
        googleError: "No se ha podido entrar con Google",
        emailYaRegistrado: "Este correo ya está registrado",
        usuarioEliminado: "Usuario eliminado, no puedes iniciar sesión",
        usuarioEliminadoRecuperar: "Usuario eliminado, no puedes recuperar la contraseña",
        sesionCerrada: "Sesión cerrada",
        cuentaEliminada: "Tu cuenta ha sido eliminada",
        sesionCaducada: "Tu sesión ha caducado. Vuelve a iniciar sesión",
        confirmarEliminar: "¿Eliminar al usuario {email}?",
        recuperarTitulo: "Recuperar contraseña",
        continuar: "Continuar",
        nuevaContrasenaTitulo: "Nueva contraseña",
        nuevaContrasena: "Nueva contraseña",
        confirmarContrasena: "Repite la contraseña",
        guardarContrasena: "Guardar contraseña",
        volverInicio: "Volver al inicio",
        introduceNuevaContrasena: "Escribe la nueva contraseña",
        contrasenaActualizada: "Contraseña actualizada. Ya puedes iniciar sesión",
        contrasenasNoCoinciden: "Las contraseñas no coinciden",
        vozNoDisponible: "El dictado por voz no está disponible en este navegador",
    },
    en: {
        codigo: "EN",
        login: "Login",
        registro: "Sign up",
        email: "Email",
        nick: "Username",
        contrasena: "Password",
        recordarme: "Remember me",
        olvidaste: "Forgot your password?",
        recuperar: "Recover",
        noRegistrado: "Don't have an account yet?",
        creaCuenta: "Create an account",
        entrar: "Sign in",
        yaTienes: "Already have an account?",
        iniciaSesion: "Sign in",
        crearCuenta: "Create account",
        usuarios: "Users",
        gestionUsuarios: "User management",
        etiquetaRol: "Role",
        etiquetaEstado: "Status",
        rolUsuario: "user",
        rolAdministrador: "administrator",
        estadoActivo: "active",
        estadoPendiente: "pending",
        estadoEliminado: "deleted",
        refrescar: "Refresh",
        cerrarSesion: "Log out",
        eliminar: "Delete",
        eliminarCuenta: "Delete account",
        editar: "Edit",
        editarDatos: "Edit details",
        editarTitulo: "Edit details",
        guardarCambios: "Save changes",
        volverGestion: "Back",
        nuevaContrasenaOpcional: "New password (optional)",
        datosActualizados: "Details updated",
        hacerAdministrador: "Make admin",
        confirmarHacerAdmin: "Make {email} an administrator?",
        rolActualizado: "The user is now an administrator",
        cambiarTema: "Toggle theme",
        cambiarIdioma: "Change language",
        dictar: "Dictate",
        verContrasena: "Show password",
        ocultarContrasena: "Hide password",
        cuentaCreada: "Account created. Check your email and open the link to activate it",
        cuentaConfirmada: "Account confirmed. You can sign in now",
        correoReenviado: "We have sent the confirmation email again",
        entrarGoogle: "Sign in with Google",
        reenviarConfirmacion: "Resend confirmation",
        emailParaReenviar: "Enter the email to resend the confirmation",
        googleNoConfigurado: "Google sign-in is not configured yet",
        googleError: "Google sign-in failed",
        emailYaRegistrado: "This email is already registered",
        usuarioEliminado: "Deleted user, you cannot sign in",
        usuarioEliminadoRecuperar: "Deleted user, you cannot reset the password",
        sesionCerrada: "Session closed",
        cuentaEliminada: "Your account has been deleted",
        sesionCaducada: "Your session has expired. Sign in again",
        confirmarEliminar: "Delete user {email}?",
        recuperarTitulo: "Reset password",
        continuar: "Continue",
        nuevaContrasenaTitulo: "New password",
        nuevaContrasena: "New password",
        confirmarContrasena: "Repeat the password",
        guardarContrasena: "Save password",
        volverInicio: "Back to sign in",
        introduceNuevaContrasena: "Enter the new password",
        contrasenaActualizada: "Password updated. You can sign in now",
        contrasenasNoCoinciden: "Passwords do not match",
        vozNoDisponible: "Voice dictation is not available in this browser",
    },
};

function datosUsuario(usuario, textos) {
    const rol = usuario.rol === "administrador" ? textos.rolAdministrador : textos.rolUsuario;
    const estados = {
        activo: textos.estadoActivo,
        pendiente: textos.estadoPendiente,
        eliminado: textos.estadoEliminado,
    };
    const estado = estados[usuario.estado] || usuario.estado || textos.estadoActivo;
    return {
        nombre: `${usuario.nick} (${usuario.email})`,
        meta: `${textos.etiquetaRol}: ${rol} · ${textos.etiquetaEstado}: ${estado}`,
    };
}

function pintarDatosUsuario(nodo, usuario, textos) {
    const datos = datosUsuario(usuario, textos);
    nodo.replaceChildren();
    const nombre = document.createElement("span");
    nombre.className = "usuario-nombre";
    nombre.textContent = datos.nombre;
    const meta = document.createElement("span");
    meta.className = "usuario-meta";
    meta.textContent = datos.meta;
    nodo.append(nombre, meta);
}

function aplicarTextos(raiz, textos) {
    raiz.querySelectorAll("[data-texto]").forEach((nodo) => {
        const valor = textos[nodo.dataset.texto];
        if (valor) {
            nodo.textContent = valor;
        }
    });
    raiz.querySelectorAll("[data-etiqueta]").forEach((nodo) => {
        const valor = textos[nodo.dataset.etiqueta];
        if (valor) {
            nodo.setAttribute("aria-label", valor);
        }
    });
}
