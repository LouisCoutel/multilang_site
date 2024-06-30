const openBtn = document.getElementById("open-assistant");

// il faut que la fenêtre de chat soit insérée dans le DOM pour pouvoir déclarer les eventListeners.
openBtn.onclick = () => {
	// Il y a un bug dans HTMX avec 'hx-swap-oob' qui m'oblige à utiliser un eventListener pour déclencher le défilement plutot que 'scroll:bottom'
	// https://github.com/bigskysoftware/htmx/issues/1882
	document.addEventListener("htmx:wsAfterMessage", (e) => {
		const messagesDiv = document.getElementById("messages");
		messagesDiv.scrollTop = messagesDiv.scrollHeight;
	});

	setTimeout(() => {
		const assistant = document.getElementById("assistant-window");
		const collapseBtn = document.getElementById("collapse-assistant");

		collapseBtn.onclick = () => {
			assistant.classList.toggle("collapsed");

			if (collapseBtn.innerHTML === gettext("Show")) {
				collapseBtn.innerHTML = gettext("Hide");
			} else {
				collapseBtn.innerHTML = gettext("Show");
			}

			if (assistant.classList.contains("hidden")) {
				assistant.classList.remove("hidden");
				collapseBtn.classList.remove("collapsed");
			} else {
				setTimeout(() => {
					collapseBtn.classList.add("collapsed");
					assistant.classList.add("hidden");
				}, 500);
			}
		};
	}, 500);
};
