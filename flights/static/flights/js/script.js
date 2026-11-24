// Mobile navigation

const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

menuBtn.addEventListener("click", () => {
    navLinks.classList.toggle("show");
});


// Swap source and destination

const swapBtn = document.getElementById("swapBtn");

const source = document.getElementById("source");
const destination = document.getElementById("destination");

swapBtn.addEventListener("click", () => {

    const temp = source.value;

    source.value = destination.value;
    destination.value = temp;

});


// Prevent selecting past dates

const departure = document.getElementById("departure");

const today = new Date();
const localDate = new Date(
    today.getTime() - today.getTimezoneOffset() * 60000
).toISOString().split("T")[0];

departure.min = localDate;


// Validate flight search

const form = document.getElementById("flightSearchForm");

form.addEventListener("submit", (event) => {

    if (source.value === destination.value) {

        event.preventDefault();

        alert("Source and destination cannot be the same.");

        return;
    }

    if (!source.value || !destination.value || !departure.value) {

        event.preventDefault();

        alert("Please fill in all required fields.");

    }

});