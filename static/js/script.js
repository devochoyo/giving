const form = document.getElementById("supportForm");

if (form) {
  const button = document.getElementById("payButton");
  const errorBox = document.getElementById("errorBox");

  form.addEventListener("submit", function (event) {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const amount = parseFloat(document.getElementById("amount").value);

    let message = "";

    if (name.length < 3) {
      message = "Please enter your full name.";
    } else if (!email.includes("@") || !email.includes(".")) {
      message = "Please enter a valid email address.";
    } else if (isNaN(amount) || amount <= 0) {
      message = "Please enter an amount greater than zero.";
    }

    if (message !== "") {
      event.preventDefault();
      errorBox.textContent = message;
      errorBox.style.display = "block";
      return;
    }

    errorBox.style.display = "none";
    button.disabled = true;
    button.textContent = "Taking you to secure checkout...";
  });
}

// the browser back button can bring the page back with the button stuck
window.addEventListener("pageshow", function () {
  const button = document.getElementById("payButton");
  if (button) {
    button.disabled = false;
    button.textContent = "Continue to Payment";
  }
});
