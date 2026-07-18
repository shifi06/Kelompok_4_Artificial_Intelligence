document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("clickMe");
    const output = document.getElementById("output");

    btn.addEventListener("click", () => {
        output.textContent = "Button clicked! 🎉";
    });
});
