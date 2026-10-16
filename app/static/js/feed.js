document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post");
            const tipo = this.getAttribute("data-type");

            fetch(`/reaction/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ tipo })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data.reacciones) return;

                const countsDiv = document.getElementById(
                    `reaction-counts-${postId}`
                );

                if (!countsDiv) return;

                countsDiv.textContent = [
                    `👍 ${data.reacciones.like || 0}`,
                    `❤️ ${data.reacciones.love || 0}`,
                    `😂 ${data.reacciones.haha || 0}`,
                    `😮 ${data.reacciones.wow || 0}`,
                    `😢 ${data.reacciones.sad || 0}`,
                    `😡 ${data.reacciones.angry || 0}`
                ].join(" ");
            })
            .catch(error => console.error("Error:", error));
        });
    });
});
