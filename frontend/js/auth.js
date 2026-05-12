if (getToken()) {
  window.location.href = "/";
}

const tabs = document.querySelectorAll(".tab");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const errorEl = document.getElementById("error-message");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.toggle("active", t === tab));
    const which = tab.dataset.tab;
    loginForm.classList.toggle("hidden", which !== "login");
    registerForm.classList.toggle("hidden", which !== "register");
    errorEl.classList.add("hidden");
  });
});

function showError(message) {
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.classList.add("hidden");
  const data = new FormData(loginForm);
  try {
    const result = await api.login(data.get("email"), data.get("password"));
    setToken(result.access_token);
    window.location.href = "/";
  } catch (err) {
    showError(err.message);
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.classList.add("hidden");
  const data = new FormData(registerForm);
  const email = data.get("email");
  const password = data.get("password");
  try {
    await api.register(email, password);

    // --- Manual sign-in flow (ACTIVE) -----------------------------------
    // After register, switch to the Sign-in tab and pre-fill the email so
    // the user manually logs in. Useful for testing the login flow.
    // To restore auto-login, comment out these 3 lines AND uncomment the
    // 3 lines in the "Auto-login flow" block below.
    document.querySelector('.tab[data-tab="login"]').click();
    loginForm.email.value = email;
    loginForm.password.focus();
    // --------------------------------------------------------------------

    // --- Auto-login flow (INACTIVE) -------------------------------------
    // Uncomment these 3 lines (and comment the manual flow above) to make
    // registration log the user in immediately and redirect to /.
    // const result = await api.login(email, password);
    // setToken(result.access_token);
    // window.location.href = "/";
    // --------------------------------------------------------------------
  } catch (err) {
    showError(err.message);
  }
});
