// Function to send message
function sendMessage() {
  const userQuery = document.getElementById("userQuery").value;
  if (userQuery.trim() === "") return;

  const chatBox = document.getElementById("chatBox");

  // Display user message
  const userDiv = document.createElement("div");
  userDiv.classList.add("user-input");
  userDiv.innerHTML = `<strong>Anda:</strong> ${userQuery}`;
  chatBox.appendChild(userDiv);

  // Clear input
  document.getElementById("userQuery").value = "";

  // Scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  // Display AI response with typing animation
  setTimeout(() => {
    const aiDiv = document.createElement("div");
    aiDiv.classList.add("ai-response");

    // Create a unique container for typing animation
    const typingText = document.createElement("span");
    typingText.id = "typing-text";
    aiDiv.innerHTML = `<strong>YouFin AI:</strong> `;
    aiDiv.appendChild(typingText);

    chatBox.appendChild(aiDiv);

    // Start typing animation
    const aiResponseText =
      "Terima kasih atas pertanyaannya. Berikut saran yang dapat membantu Anda...";
    typeResponse(aiResponseText, typingText);

    // Scroll to bottom again after AI response starts
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 1000); // Delay of 1 second
}

// Function to create typing animation
function typeResponse(text, element) {
  let index = 0;
  const typingSpeed = 25; // Adjust typing speed in milliseconds

  const typingInterval = setInterval(() => {
    element.innerHTML += text[index];
    index++;

    // Scroll chat box as text appears
    element.parentElement.parentElement.scrollTop =
      element.parentElement.parentElement.scrollHeight;

    if (index === text.length) {
      clearInterval(typingInterval); // Stop typing animation when done
    }
  }, typingSpeed);
}

// Event listener for the send button
document.getElementById("sendBtn").addEventListener("click", sendMessage);

// Event listener for Enter key
document
  .getElementById("userQuery")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent default form submission
      sendMessage();
    }
  });

// Autofocus on input when page loads
window.onload = () => {
  document.getElementById("userQuery").focus();
};
