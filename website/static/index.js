function deleteNote(clientId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ clientId: clientId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }