let formHasFocus = false;

// Function to set focus flag when form input is focused
document.getElementById('create-campaign-form').addEventListener('focusin', function () {
formHasFocus = true;
});

// Function to check form focus and show alert if navigating away
function handleClick() {
if (formHasFocus) {
    // User is navigating away, show alert
    alert("You started filling out the form. Are you sure you want to leave?");
} else {
    // User is submitting the form
    document.getElementById('create-campaign-form').submit();
}
}
// Detect changes in the URL
window.addEventListener('popstate', function () {
// Check if the form has focus when the URL changes
if (formHasFocus) {
    // User is navigating away, show alert
    alert("You started filling out the form. Are you sure you want to leave?");
}
});

// Get all links and buttons on the page
const links = document.querySelectorAll('a');
const buttons = document.querySelectorAll('button');

// Add onclick attribute to all links
links.forEach(link => {
    link.setAttribute('onclick', 'handleClick()');
});

// Add onclick attribute to all buttons
buttons.forEach(button => {
    button.setAttribute('onclick', 'handleClick()');
});

var currentTab = 0; // Current tab is set to be the first tab (0)
        showTab(currentTab); // Display the current tab
        
        function showTab(n) {
          // This function will display the specified tab of the form...
          var x = document.getElementsByClassName("step");
          x[n].style.display = "block";
          //... and fix the Previous/Next buttons:
          if (n == 0) {
            document.getElementById("prevBtn").style.display = "none";
          } else {
            document.getElementById("prevBtn").style.display = "inline";
          }
          if (n == (x.length - 1)) {
            document.getElementById("nextBtn").innerHTML = "Submit";
          } else {
            document.getElementById("nextBtn").innerHTML = "Next";
          }
          //... and run a function that will display the correct step indicator:
          fixStepIndicator(n)
        }
        
        function nextPrev(n) {
          // This function will figure out which tab to display
          var x = document.getElementsByClassName("step");
          // Exit the function if any field in the current tab is invalid:
          if (n == 1 && !validateForm()) return false;
          // Hide the current tab:
          x[currentTab].style.display = "none";
          // Increase or decrease the current tab by 1:
          currentTab = currentTab + n;
          // if you have reached the end of the form...
          if (currentTab >= x.length) {
            // ... the form gets submitted:
            document.getElementById("signUpForm").submit();
            return false;
          }
          // Otherwise, display the correct tab:
          showTab(currentTab);
        }
        
        function validateForm() {
          // This function deals with validation of the form fields
          var x, y, i, valid = true;
          x = document.getElementsByClassName("step");
          y = x[currentTab].getElementsByTagName("input");
          // A loop that checks every input field in the current tab:
          for (i = 0; i < y.length; i++) {
            // If a field is empty...
            if (y[i].value == "") {
              // add an "invalid" class to the field:
              y[i].className += " invalid";
              // and set the current valid status to false
              valid = false;
            }
          }
          // If the valid status is true, mark the step as finished and valid:
          if (valid) {
            document.getElementsByClassName("stepIndicator")[currentTab].className += " finish";
          }
          return valid; // return the valid status
        }
        
        function fixStepIndicator(n) {
          // This function removes the "active" class of all steps...
          var i, x = document.getElementsByClassName("stepIndicator");
          for (i = 0; i < x.length; i++) {
            x[i].className = x[i].className.replace(" active", "");
          }
          //... and adds the "active" class on the current step:
          x[n].className += " active";
        }