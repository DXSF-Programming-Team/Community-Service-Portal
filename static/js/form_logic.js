const student_first_name = document.getElementsByName("student_first_name")[0];
const student_last_name = document.getElementsByName("student_last_name")[0];
const graduation_year = document.getElementsByName("graduation_year")[0];
const student_email = document.getElementsByName("student_email")[0];
        
function autofillEmail() {
    if (student_first_name.value && student_last_name.value && graduation_year.value) {
    const email = graduation_year.value.toString().toLowerCase().slice(2, 4) + 
                student_last_name.value.toLowerCase().slice(0, 4) +
                student_first_name.value.toLowerCase().slice(0, 2) + "@dextersouthfield.org";
            student_email.value = email;
        }
    }

student_first_name.addEventListener("input", autofillEmail);
student_last_name.addEventListener("input", autofillEmail);
graduation_year.addEventListener("input", autofillEmail);

// dates are zero-indexed
function addServiceDate() {
    const serviceDateContainer = document.getElementById("service_date_container");
    const newIndex = serviceDateContainer.children.length;
    const newRow = document.createElement("div");
    newRow.className = "service_date_row";
    newRow.id = "service_date_row_" + newIndex;
    serviceDateContainer.appendChild(newRow);

    const newServiceDate = document.createElement("input");
    newServiceDate.type = "date";
    newServiceDate.name = "service_date_input_" + newIndex;
    newServiceDate.id = "service_date_input_" + newIndex;
    newServiceDate.placeholder = "Date of service";
    newServiceDate.required = true;
    newRow.appendChild(newServiceDate);

    const newRemoveButton = document.createElement("button");
    newRemoveButton.type = "button";
    newRemoveButton.id = "remove_service_date_button_" + newIndex;
    newRemoveButton.name = "remove_service_date_button_" + newIndex;
    newRemoveButton.className = "btn btn-date-remove";
    newRemoveButton.onclick = function() { removeServiceDate(newIndex); };
    newRemoveButton.innerHTML = "<i class='bi bi-trash'></i>";
    newRow.appendChild(newRemoveButton);
}

function removeServiceDate(index) {
    const serviceDateContainer = document.getElementById("service_date_container");
    console.log("Removing service date " + index);
    const dateRow = document.getElementById("service_date_row_" + index);
    dateRow.remove();
            
    // Reindex remaining elements
    let newIndex = 0;
    Array.from(serviceDateContainer.children).forEach(function(child) {
        const currentIndex = newIndex;
        const row = child;
        console.log("Processing row " + newIndex);
        row.id = "service_date_row_" + currentIndex;
        row.name = "service_date_row_" + currentIndex;
                
        Array.from(row.children).forEach(function(child) {
            const childId = child.id;
            console.log("Child ID: " + childId);
                    
            if (childId && childId.includes("service_date_input_")) {
                child.name = "service_date_input_" + currentIndex;
                child.id = "service_date_input_" + currentIndex;
            } else if (childId && childId.includes("remove_service_date_button_")) {
                child.name = "remove_service_date_button_" + currentIndex;
                child.id = "remove_service_date_button_" + currentIndex;
                child.onclick = function() { removeServiceDate(currentIndex); };
                console.log(`Setting onclick for remove service date ${currentIndex}. Will call removeServiceDate(${currentIndex})`);
            }
        });
        newIndex++;
    });
}

function searchFaculty() {
    var facultyList = document.getElementsByClassName("faculty-list")[0];
    var facultyListItems = facultyList.getElementsByTagName("li");
    var searchInput = document.getElementsByName("contact_search")[0].value.toLowerCase();

    for (var i = 0; i < facultyListItems.length; i++) {
        facultyListItems[i].style.backgroundColor = "";
    }
            
    if (searchInput.length < 2) {
        facultyList.style.display = "none";
        return;
    } else {
        facultyList.style.display = "";
    }

    for (var i = 0; i < facultyListItems.length; i++) {
        var facultyListItem = facultyListItems[i];
        var facultyName = facultyListItem.querySelector("h4").textContent.toLowerCase();
        var facultyTitle = facultyListItem.querySelector("p").textContent.toLowerCase();
        var facultyEmail = facultyListItem.querySelectorAll("p")[1].textContent.toLowerCase();
        
        if (facultyName.includes(searchInput) || facultyTitle.includes(searchInput) || facultyEmail.includes(searchInput)) {
            facultyListItem.style.display = "";
        } else {
            facultyListItem.style.display = "none";
        }
    }
}

function selectFaculty(facultyListItem) {
    const name = facultyListItem.querySelector("h4").textContent;
    const email = facultyListItem.querySelectorAll("p")[1].textContent;
    const contactEmail = document.getElementsByName("contact_email")[0];
    contactEmail.value = email;
    const contactNameHidden = document.getElementsByName("contact_name_hidden")[0];
    contactNameHidden.value = name;
    const contactSearch = document.getElementsByName("contact_search")[0];
    contactSearch.value = name;
    
    for (var i = 0; i < facultyListItem.parentNode.children.length; i++) {
        if (facultyListItem.parentNode.children[i] !== facultyListItem) {
            facultyListItem.parentNode.children[i].style.display = "none";
        }
    }
    facultyListItem.style.backgroundColor = "#f0f0f0";
}