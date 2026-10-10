document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function () {
            let postId = this.getAttribute("data-post");
            let tipo = this.getAttribute("data-type");

            fetch(`/reaction/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ tipo: tipo })
            })
            .then(response => response.json())
            .then(data => {
                if (data.reacciones) {
                    let countsDiv = document.getElementById(`reaction-counts-${postId}`);
                    countsDiv.innerHTML = `
                        👍 ${data.reacciones.like || 0}
                        ❤️ ${data.reacciones.love || 0}
                        😂 ${data.reacciones.haha || 0}
                        😮 ${data.reacciones.wow || 0}
                        😢 ${data.reacciones.sad || 0}
                        😡 ${data.reacciones.angry || 0}
                    `;
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});