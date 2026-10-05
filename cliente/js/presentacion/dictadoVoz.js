class DictadoVoz {
    constructor() {
        const Reconocimiento = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.disponible = Boolean(Reconocimiento);
        this.reconocimiento = this.disponible ? new Reconocimiento() : null;
        if (this.reconocimiento) {
            this.reconocimiento.interimResults = false;
            this.reconocimiento.maxAlternatives = 1;
        }
    }

    dictar(campo, idioma, alError) {
        if (!this.disponible || !campo) {
            alError();
            return;
        }
        this.reconocimiento.lang = idioma === "en" ? "en-US" : "es-ES";
        this.reconocimiento.onresult = (evento) => {
            campo.value = evento.results[0][0].transcript;
            campo.focus();
        };
        this.reconocimiento.onerror = () => alError();
        try {
            this.reconocimiento.start();
        } catch {
            alError();
        }
    }
}
