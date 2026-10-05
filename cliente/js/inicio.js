const rest = new ClienteRest(new ClienteHttp());
const cw = new ControlWeb(rest);
cw.iniciar();
