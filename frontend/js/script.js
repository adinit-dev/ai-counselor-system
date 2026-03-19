// LOGIN FUNCTION
async function login(){

const role = document.querySelector('input[name="role"]:checked').value;

const email = document.getElementById("email").value;
const password = document.getElementById("password").value;
const BASE_URL = "https://ai-counselor-system.onrender.com";

let url;

if(role === "student"){
    url = "/login";
}else{
    url = "/counselor_login";
}

const response = await fetch(`${BASE_URL}${url}`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        email: email,
        password: password
    })
});

const data = await response.json();

if(data.status === "success"){

if(role === "student"){

localStorage.setItem("student_id",data.id);
localStorage.setItem("student_name",data.name);

window.location.href="student/dashboard.html";

}
else{

localStorage.setItem("counselor_id",data.id);

window.location.href="counselor/dashboard.html";

}

}
else{

alert("Invalid login credentials");

}

}


// LOGOUT
function logout(){

localStorage.clear();
window.location.href = "../index.html";

}



// LOAD AVAILABLE TESTS
async function loadTests() {

    const response = await fetch(`${BASE_URL}/tests`);
    const data = await response.json();

    let html = "";

    data.tests.forEach(test => {

        html += `
        <div class="test-card">
            <h3>${test.name}</h3>
            <button onclick="startTest(${test.id})">
                Start Test
            </button>
        </div>
        `;
    });

    document.getElementById("testsContainer").innerHTML = html;
}


// START TEST
function startTest(id){

window.location.href = "test.html?test_id=" + id;

}


// run automatically when dashboard loads
if(document.getElementById("tests")){
loadTests();
}
