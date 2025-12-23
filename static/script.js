async function enviar() {
    const entrada = document.getElementById("entrada");
    const texto = entrada.value.trim();
    if (!texto) return;

    adicionar("Você", texto, "usuario");
    entrada.value = "";

    const resposta = await fetch("/mensagem", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({texto})
    });

    const dados = await resposta.json();
    adicionar("Jarbas", dados.resposta, "jarbas");
}

function adicionar(nome, texto, classe) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.className = "msg " + classe;
    div.innerHTML = `<strong>${nome}:</strong> ${texto}`;
    chat.appendChild(div);
    window.scrollTo(0, document.body.scrollHeight);
}
