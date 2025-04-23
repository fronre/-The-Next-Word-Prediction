function predictNextWord() {
    const input = document.getElementById("userInput").value;

    if (input.trim() !== "") {
        fetch(`/predict?text=${encodeURIComponent(input)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Predictions:", data.predicted_text);
                // عرض الاقتراحات في واجهة المستخدم
            })
            .catch(error => console.error("Error:", error));
    }
}
