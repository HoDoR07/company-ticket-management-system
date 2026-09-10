/* =========================================================
   AUTHENTICATION
========================================================= */

function getToken() {
    return localStorage.getItem("access_token");
}

function authHeaders() {
    const token = getToken();

    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}


/* =========================================================
   LOGOUT
========================================================= */

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login-page";
}


/* =========================================================
   LOGIN
========================================================= */

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {

            const response = await fetch("/login", {
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

            if (!response.ok) {
                alert(data.detail || "Login failed");
                return;
            }

            localStorage.setItem(
                "access_token",
                data.access_token
            );

            const token = data.access_token;

            const payload = JSON.parse(
                atob(token.split(".")[1])
            );

            const role = payload.role;

            if (role === "employee") {
                window.location.href = "/static/employee.html";
            }
            else if (role === "technician") {
                window.location.href = "/static/technician.html";
            }
            else if (role === "admin") {
                window.location.href = "/static/admin.html";
            }
            else {
                alert("Invalid user role");
            }

        }
        catch (error) {

            console.error(error);
            alert("Something went wrong.");

        }

    });

}


/* =========================================================
   REGISTER
========================================================= */

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const name = document.getElementById("name").value;
        const email = document.getElementById("registerEmail").value;
        const phone = document.getElementById("phone").value;
        const password = document.getElementById("registerPassword").value;

        try {

            const response = await fetch("/users/new", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    phone: phone || null,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {

                alert(
                    data.detail ||
                    "Registration failed"
                );

                return;
            }

            alert(
                "Account created successfully. Please login."
            );

            window.location.href = "/login-page";

        }
        catch (error) {

            console.error(error);
            alert("Something went wrong.");

        }

    });

}


/* =========================================================
   EMPLOYEE PROFILE
========================================================= */

async function loadEmployeeProfile() {

    const profile =
        document.getElementById("employeeProfile");

    if (!profile) {
        return;
    }

    try {

        const response = await fetch(
            "/users/me",
            {
                method: "GET",
                headers: authHeaders()
            }
        );

        const data = await response.json();

        if (!response.ok) {

            profile.innerHTML =
                "Unable to load profile.";

            return;
        }

        // Store profile data for Edit Profile
        window.currentEmployeeProfile = data;

        profile.innerHTML = `
            <p><strong>Name:</strong> ${data.name}</p>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Phone:</strong> ${data.phone || "-"}</p>
            <p><strong>Role:</strong> ${data.role}</p>
        `;

    }
    catch (error) {

        console.error(error);

        profile.innerHTML =
            "Unable to load profile.";

    }

}


/* =========================================================
   EMPLOYEE EDIT PROFILE
========================================================= */

function editEmployeeProfile() {

    const user =
        window.currentEmployeeProfile;

    if (!user) {

        alert(
            "Profile data is not loaded."
        );

        return;
    }

    const name = prompt(
        "Enter your name:",
        user.name
    );

    if (name === null) {
        return;
    }

    const email = prompt(
        "Enter your email:",
        user.email
    );

    if (email === null) {
        return;
    }

    const phone = prompt(
        "Enter your phone:",
        user.phone || ""
    );

    if (phone === null) {
        return;
    }

    updateEmployeeProfile(
        name,
        email,
        phone
    );
}


async function updateEmployeeProfile(
    name,
    email,
    phone
) {

    const user =
        window.currentEmployeeProfile;

    try {

        const response = await fetch(
            `/users/${user.id}`,
            {
                method: "PUT",
                headers: authHeaders(),
                body: JSON.stringify({
                    name: name,
                    email: email,
                    phone: phone || null
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Profile update failed"
            );

            return;
        }

        window.currentEmployeeProfile = data;

        alert(
            "Profile updated successfully."
        );

        loadEmployeeProfile();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   EMPLOYEE CREATE TICKET
========================================================= */

const ticketForm =
    document.getElementById("ticketForm");

if (ticketForm) {

    ticketForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const title =
                document.getElementById(
                    "ticketTitle"
                ).value;

            const description =
                document.getElementById(
                    "ticketDescription"
                ).value;

            try {

                const response =
                    await fetch(
                        "/tickets",
                        {
                            method: "POST",
                            headers: authHeaders(),
                            body: JSON.stringify({
                                title: title,
                                description: description
                            })
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    alert(
                        data.detail ||
                        "Ticket creation failed"
                    );

                    return;
                }

                alert(
                    "Ticket created successfully."
                );

                ticketForm.reset();

                loadEmployeeTickets();

            }
            catch (error) {

                console.error(error);

                alert(
                    "Something went wrong."
                );

            }

        }
    );

}


/* =========================================================
   EMPLOYEE LOAD TICKETS
========================================================= */

async function loadEmployeeTickets() {

    const container =
        document.getElementById(
            "employeeTickets"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await fetch(
                "/tickets",
                {
                    method: "GET",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            container.innerHTML =
                `<p>${data.detail ||
                "Unable to load tickets."}</p>`;

            return;
        }

        if (!data.length) {

            container.innerHTML =
                "<p>No tickets found.</p>";

            return;
        }

        container.innerHTML = "";

        data.forEach(ticket => {

            const ticketCard =
                document.createElement("div");

            ticketCard.className =
                "ticket-card";

            ticketCard.innerHTML = `
                <h3>
                    ${ticket.title}
                </h3>

                <p>
                    ${ticket.description}
                </p>

                <div class="ticket-meta">

                    <span class="badge">
                        ID: ${ticket.id}
                    </span>

                    <span class="badge">
                        Priority: ${ticket.priority}
                    </span>

                    <span class="badge">
                        Status: ${ticket.status}
                    </span>

                    <span class="badge">
                        Assigned To:
                        ${ticket.assigned_to ||
                        "Not Assigned"}
                    </span>

                </div>

                <button
                    class="secondary-btn"
                    onclick="updateEmployeeTicket(
                        ${ticket.id},
                        '${escapeQuotes(ticket.title)}',
                        '${escapeQuotes(ticket.description)}'
                    )"
                >
                    Update
                </button>

                <button
                    class="secondary-btn"
                    onclick="deleteEmployeeTicket(
                        ${ticket.id}
                    )"
                >
                    Delete
                </button>
            `;

            container.appendChild(ticketCard);

        });

    }
    catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load tickets.</p>";

    }

}


/* =========================================================
   ESCAPE QUOTES
========================================================= */

function escapeQuotes(value) {

    return String(value)
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'")
        .replace(/\n/g, "\\n")
        .replace(/\r/g, "\\r");

}


/* =========================================================
   EMPLOYEE UPDATE TICKET
========================================================= */

async function updateEmployeeTicket(
    ticketId,
    oldTitle,
    oldDescription
) {

    const title =
        prompt(
            "Enter new title:",
            oldTitle
        );

    if (title === null) {
        return;
    }

    const description =
        prompt(
            "Enter new description:",
            oldDescription
        );

    if (description === null) {
        return;
    }

    try {

        const response =
            await fetch(
                `/tickets/update/${ticketId}`,
                {
                    method: "PUT",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        title: title,
                        description: description
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Ticket update failed"
            );

            return;
        }

        alert(
            "Ticket updated successfully."
        );

        loadEmployeeTickets();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   EMPLOYEE DELETE TICKET
========================================================= */

async function deleteEmployeeTicket(ticketId) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this ticket?"
        );

    if (!confirmDelete) {
        return;
    }

    try {

        const response =
            await fetch(
                `/ticket/delete/${ticketId}`,
                {
                    method: "DELETE",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Ticket deletion failed"
            );

            return;
        }

        alert(
            "Ticket deleted successfully."
        );

        loadEmployeeTickets();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   TECHNICIAN LOAD TICKETS
========================================================= */

async function loadTechnicianTickets() {

    const container =
        document.getElementById(
            "technicianTickets"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await fetch(
                "/technician/tickets",
                {
                    method: "GET",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            container.innerHTML =
                `<p>${data.detail ||
                "Unable to load tickets."}</p>`;

            return;
        }

        if (!data.length) {

            container.innerHTML =
                "<p>No assigned tickets found.</p>";

            return;
        }

        container.innerHTML = "";

        data.forEach(ticket => {

            const ticketCard =
                document.createElement("div");

            ticketCard.className =
                "ticket-card";

            ticketCard.innerHTML = `
                <h3>
                    ${ticket.title}
                </h3>

                <p>
                    ${ticket.description}
                </p>

                <div class="ticket-meta">

                    <span class="badge">
                        ID: ${ticket.id}
                    </span>

                    <span class="badge">
                        Priority: ${ticket.priority}
                    </span>

                    <span class="badge">
                        Status: ${ticket.status}
                    </span>

                    <span class="badge">
                        Created By:
                        ${ticket.created_by}
                    </span>

                </div>

                ${
                    ticket.status !== "closed"
                    ?
                    `
                        <button
                            class="secondary-btn"
                            onclick="updateTechnicianTicket(
                                ${ticket.id},
                                'in progress'
                            )"
                        >
                            In Progress
                        </button>

                        <button
                            class="secondary-btn"
                            onclick="updateTechnicianTicket(
                                ${ticket.id},
                                'resolved'
                            )"
                        >
                            Resolved
                        </button>
                    `
                    :
                    ""
                }
            `;

            container.appendChild(ticketCard);

        });

    }
    catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load tickets.</p>";

    }

}


/* =========================================================
   TECHNICIAN STATUS UPDATE
========================================================= */

async function updateTechnicianTicket(
    ticketId,
    newStatus
) {

    try {

        const response =
            await fetch(
                `/technician/tickets/${ticketId}`,
                {
                    method: "PATCH",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        status: newStatus
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Status update failed"
            );

            return;
        }

        alert(
            `Ticket marked as ${newStatus}.`
        );

        loadTechnicianTickets();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN DASHBOARD
========================================================= */

async function loadAdminDashboard() {

    const totalUsers =
        document.getElementById(
            "totalUsers"
        );

    if (!totalUsers) {
        return;
    }

    try {

        const response =
            await fetch(
                "/admin/dashboard",
                {
                    method: "GET",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to load dashboard"
            );

            return;
        }

        document.getElementById(
            "totalUsers"
        ).textContent =
            data.total_users;

        document.getElementById(
            "totalTickets"
        ).textContent =
            data.total_tickets;

        document.getElementById(
            "openTickets"
        ).textContent =
            data.open_tickets;

        document.getElementById(
            "progressTickets"
        ).textContent =
            data.in_progress_tickets;

        document.getElementById(
            "resolvedTickets"
        ).textContent =
            data.resolved_tickets;

        document.getElementById(
            "closedTickets"
        ).textContent =
            data.closed_tickets;

    }
    catch (error) {

        console.error(error);

    }

}


/* =========================================================
   ADMIN USERS
========================================================= */

async function loadAdminUsers() {

    const container =
        document.getElementById(
            "adminUsers"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await fetch(
                "/admin/alluser",
                {
                    method: "GET",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            container.innerHTML =
                `<p>${data.detail ||
                "Unable to load users."}</p>`;

            return;
        }

        if (!data.length) {

            container.innerHTML =
                "<p>No users found.</p>";

            return;
        }

        let tableHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Role</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>
        `;

        data.forEach(user => {

            tableHTML += `
                <tr>

                    <td>
                        ${user.id}
                    </td>

                    <td>
                        ${user.name}
                    </td>

                    <td>
                        ${user.email}
                    </td>

                    <td>
                        ${user.phone || "-"}
                    </td>

                    <td>
                        ${user.role}
                    </td>

                    <td>

                        <button
                            class="secondary-btn"
                            onclick="updateUserRole(${user.id})"
                        >
                            Update Role
                        </button>

                        <button
                            class="secondary-btn"
                            onclick="deleteAdminUser(${user.id})"
                        >
                            Delete
                        </button>

                    </td>

                </tr>
            `;

        });

        tableHTML += `
                </tbody>
            </table>
        `;

        container.innerHTML =
            tableHTML;

    }
    catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load users.</p>";

    }

}


/* =========================================================
   ADMIN UPDATE USER ROLE
========================================================= */

async function updateUserRole(userId) {

    const role =
        prompt(
            "Enter role: admin, technician, employee"
        );

    if (role === null) {
        return;
    }

    const selectedRole =
        role.trim().toLowerCase();

    if (
        selectedRole !== "admin" &&
        selectedRole !== "technician" &&
        selectedRole !== "employee"
    ) {

        alert(
            "Please enter admin, technician, or employee."
        );

        return;
    }

    try {

        const response =
            await fetch(
                `/admin/users/${userId}`,
                {
                    method: "PUT",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        role: selectedRole
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Role update failed"
            );

            return;
        }

        alert(
            "User role updated successfully."
        );

        loadAdminUsers();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN DELETE USER
========================================================= */

async function deleteAdminUser(userId) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this user?"
        );

    if (!confirmDelete) {
        return;
    }

    try {

        const response =
            await fetch(
                `/admin/user/${userId}/delete`,
                {
                    method: "DELETE",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "User deletion failed"
            );

            return;
        }

        alert(
            "User deleted successfully."
        );

        loadAdminUsers();
        loadAdminDashboard();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN LOAD TICKETS
========================================================= */

async function loadAdminTickets() {

    const container =
        document.getElementById(
            "adminTickets"
        );

    if (!container) {
        return;
    }

    const status =
        document.getElementById(
            "adminStatusFilter"
        )?.value || "";

    const priority =
        document.getElementById(
            "adminPriorityFilter"
        )?.value || "";

    let url =
        "/admin/tickets";

    const params = [];

    if (status) {

        params.push(
            `ticket_status=${encodeURIComponent(status)}`
        );

    }

    if (priority) {

        params.push(
            `ticket_priority=${encodeURIComponent(priority)}`
        );

    }

    if (params.length > 0) {

        url += "?" + params.join("&");

    }

    try {

        const response =
            await fetch(
                url,
                {
                    method: "GET",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            container.innerHTML =
                `<p>${data.detail ||
                "Unable to load tickets."}</p>`;

            return;
        }

        if (!data.length) {

            container.innerHTML =
                "<p>No tickets found.</p>";

            return;
        }

        let tableHTML = `
            <table class="data-table">

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Created By</th>
                        <th>Assigned To</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>
        `;

        data.forEach(ticket => {

            tableHTML += `
                <tr>

                    <td>
                        ${ticket.id}
                    </td>

                    <td>
                        ${ticket.title}
                    </td>

                    <td>
                        ${ticket.status}
                    </td>

                    <td>
                        ${ticket.priority}
                    </td>

                    <td>
                        ${ticket.created_by}
                    </td>

                    <td>
                        ${ticket.assigned_to ||
                        "Not Assigned"}
                    </td>

                    <td>

                        ${
                            ticket.status !== "closed"
                            ?
                            `
                                <button
                                    class="secondary-btn"
                                    onclick="assignTicket(${ticket.id})"
                                >
                                    Assign
                                </button>

                                <button
                                    class="secondary-btn"
                                    onclick="updateTicketPriority(${ticket.id})"
                                >
                                    Priority
                                </button>

                                <button
                                    class="secondary-btn"
                                    onclick="updateAdminTicketStatus(${ticket.id})"
                                >
                                    Status
                                </button>
                            `
                            :
                            ""
                        }

                        <button
                            class="secondary-btn"
                            onclick="deleteAdminTicket(${ticket.id})"
                        >
                            Delete
                        </button>

                    </td>

                </tr>
            `;

        });

        tableHTML += `
                </tbody>
            </table>
        `;

        container.innerHTML =
            tableHTML;

    }
    catch (error) {

        console.error(error);

        container.innerHTML =
            "<p>Unable to load tickets.</p>";

    }

}


/* =========================================================
   ADMIN ASSIGN TICKET
========================================================= */

async function assignTicket(ticketId) {

    const technicianId =
        prompt(
            "Enter Technician User ID:"
        );

    if (technicianId === null) {
        return;
    }

    if (!technicianId.trim()) {

        alert(
            "Technician ID is required."
        );

        return;
    }

    try {

        const response =
            await fetch(
                `/ticket/${ticketId}/assign`,
                {
                    method: "POST",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        technician_id:
                            Number(technicianId)
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Ticket assignment failed"
            );

            return;
        }

        alert(
            "Ticket assigned successfully."
        );

        loadAdminTickets();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN UPDATE PRIORITY
========================================================= */

async function updateTicketPriority(ticketId) {

    const priority =
        prompt(
            "Enter priority: modrate, medium, high"
        );

    if (priority === null) {
        return;
    }

    const selectedPriority =
        priority.trim().toLowerCase();

    if (
        selectedPriority !== "modrate" &&
        selectedPriority !== "medium" &&
        selectedPriority !== "high"
    ) {

        alert(
            "Please enter modrate, medium, or high."
        );

        return;
    }

    try {

        const response =
            await fetch(
                `/admin/ticket/${ticketId}/priority`,
                {
                    method: "PUT",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        priority:
                            selectedPriority
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Priority update failed"
            );

            return;
        }

        alert(
            "Ticket priority updated successfully."
        );

        loadAdminTickets();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN UPDATE STATUS
========================================================= */

async function updateAdminTicketStatus(ticketId) {

    const newStatus =
        prompt(
            "Enter status: open, in progress, resolved, closed"
        );

    if (newStatus === null) {
        return;
    }

    const selectedStatus =
        newStatus.trim().toLowerCase();

    if (
        selectedStatus !== "open" &&
        selectedStatus !== "in progress" &&
        selectedStatus !== "resolved" &&
        selectedStatus !== "closed"
    ) {

        alert(
            "Please enter a valid status."
        );

        return;
    }

    try {

        const response =
            await fetch(
                `/admin/ticket/${ticketId}/status`,
                {
                    method: "PATCH",
                    headers: authHeaders(),
                    body: JSON.stringify({
                        status:
                            selectedStatus
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Status update failed"
            );

            return;
        }

        alert(
            "Ticket status updated successfully."
        );

        loadAdminTickets();
        loadAdminDashboard();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   ADMIN DELETE TICKET
========================================================= */

async function deleteAdminTicket(ticketId) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this ticket?"
        );

    if (!confirmDelete) {
        return;
    }

    try {

        const response =
            await fetch(
                `/admin/delete/${ticketId}/ticket`,
                {
                    method: "DELETE",
                    headers: authHeaders()
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Ticket deletion failed"
            );

            return;
        }

        alert(
            "Ticket deleted successfully."
        );

        loadAdminTickets();
        loadAdminDashboard();

    }
    catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadEmployeeProfile();
        loadEmployeeTickets();

        loadTechnicianTickets();

        loadAdminDashboard();
        loadAdminUsers();
        loadAdminTickets();

    }
);