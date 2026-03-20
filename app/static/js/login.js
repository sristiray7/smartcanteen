function switchRole(role, btn){

    const slider = document.querySelector(".switch-slider");
    const buttons = document.querySelectorAll(".switch-btn");

    const roleInput = document.getElementById("role");

    const title = document.getElementById("loginTitle");
    const subtitle = document.getElementById("loginSubtitle");

    const label = document.getElementById("loginLabel");
    const input = document.getElementById("loginInput");

    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // Clear input value when switching roles
    input.value = "";


    /* ================= ADMIN LOGIN ================= */

    if(role === "admin"){

        slider.style.left = "4px";

        roleInput.value = "admin";

        title.innerText = "Hello Admin!";
        subtitle.innerText = "Log in to your administrative account";

        label.innerText = "Email";

        input.type = "email";
        input.name = "admin_email";  // ✅ FIXED: was "email"
        input.placeholder = "Enter your email";

    }


    /* ================= USER LOGIN ================= */

    if(role === "user"){

        slider.style.left = "50%";

        roleInput.value = "user";

        title.innerText = "Hello User!";
        subtitle.innerText = "Log in to your account";

        label.innerText = "Mobile Number";

        input.type = "tel";
        input.name = "user_mobile";  // ✅ FIXED: was "mobile"
        input.placeholder = "Enter your mobile number";

    }

}


/* ================= PASSWORD TOGGLE ================= */

function togglePassword(event){

    const passwordInput = event.target.closest('.password-wrapper').querySelector('input');

    if(passwordInput.type === "password"){
        passwordInput.type = "text";
        event.target.innerText = "Hide";
    } else {
        passwordInput.type = "password";
        event.target.innerText = "Show";
    }

}


/* ================= SIGNUP FORM TOGGLE ================= */

function toggleSignupForm() {

    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const signupButton = document.querySelector(".signup-submit");

    if(loginForm.style.display === "none"){
        loginForm.style.display = "block";
        signupForm.style.display = "none";
        if(signupButton) signupButton.style.display = "block";
    } else {
        loginForm.style.display = "none";
        signupForm.style.display = "block";
        if(signupButton) signupButton.style.display = "none";
    }

}