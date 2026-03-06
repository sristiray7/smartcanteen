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


    /* ================= ADMIN LOGIN ================= */

    if(role === "admin"){

        slider.style.left = "4px";

        roleInput.value = "admin";

        title.innerText = "Hello Admin!";
        subtitle.innerText = "Log in to your administrative account";

        label.innerText = "Email";

        input.type = "email";
        input.name = "email";
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
        input.name = "mobile";
        input.placeholder = "Enter your mobile number";

    }

}