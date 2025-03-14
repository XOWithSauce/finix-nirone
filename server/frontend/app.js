// AZURE SERVER BASE URL
const BASE_URL = "http://localhost:3000/data";
const contentDiv = document.getElementById("content");
let deviceIdList = []

const getDevices = async () => {
  try {
    //console.log("Get Devices");
    const response = await fetch(`${BASE_URL}/get-devices`, {
      method: "GET",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(2000),
    });
    if (!response.ok) {
      //console.log("Could not fetch devices data.");
      deviceIdList = [1];
      renderDevicePlaceholders(1, [1]);
    } else {
      let data = await response.json();
      let { count, ids } = data.msg;
      console.log("Fetched data:\nCount: ", count, "\nIds: ", ids);
      deviceIdList = ids;
      renderDevicePlaceholders(count, ids);
    }
  } catch (err) {
    //console.log("Errors while fetching devices data: ", err);
    deviceIdList = [1];
    renderDevicePlaceholders(1, [1]);
  }
}

const getMeas = async (did) => {
  try {
    const response = await fetch(`${BASE_URL}/get-by-did?did=${did}`, {
      method: "GET",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(2000),
    });
    if (!response.ok) {
      setMeas({ label: "0", time: "0" }, did);
    } else {
      const data = await response.json();
      setMeas(data.msg, did);
    }
  } catch (err) {
    //console.log("Errors while fetching data: ", err)
    setMeas({ label: "0", time: "0" }, did);
  }
};

const setMeas = (items, deviceId) => {
  let allPTags = document.querySelectorAll(`#myDropdown${deviceId} p`);
  //console.log("setMeas allPTags: ", allPTags);
  allPTags.forEach((element, index) => {
    if (index >= items.length) {
      return;
    }
    for (const key in items) {
      if (index === 0) {
        element.textContent = items[key];
        break;
      }
      index--;
    }
  });
};

function renderDevicePlaceholders(deviceCount, deviceIds) {
  for (let i = 0; i < deviceCount; i++) {
    const dropdown = createDropdownElement(i + 1, deviceIds[i]);
    contentDiv.appendChild(dropdown);
  }
  doPolling();
}

function createDropdownElement(deviceNumber, deviceId) {
  const dropdownDiv = document.createElement("div");
  dropdownDiv.classList.add("dropdown");
  const button = document.createElement("button");
  button.classList.add("dropbtn");
  button.textContent = `Device ${deviceId}`;
  //button.onclick = function() { switchShow(this); };
  button.addEventListener("click", function() {
    switchShow(this);
  });
  const dropdownContent = document.createElement("div");
  dropdownContent.classList.add("dropdown-content");
  dropdownContent.id = `myDropdown${deviceId}`;
  const paragraph1 = document.createElement("p");
  paragraph1.classList.add("dd-element");
  paragraph1.id = "pl";
  paragraph1.textContent = "";
  const divider = document.createElement("div");
  divider.id = "divider-sm";
  const paragraph2 = document.createElement("p");
  paragraph2.classList.add("dd-element");
  paragraph2.id = "time";
  paragraph2.textContent = "";
  dropdownContent.appendChild(paragraph1);
  dropdownContent.appendChild(divider);
  dropdownContent.appendChild(paragraph2);
  dropdownDiv.appendChild(button);
  dropdownDiv.appendChild(dropdownContent);
  return dropdownDiv;
}

function doPolling() {
  //console.log("Do Polling!!!")
  function poll() {
    //console.log("poll outer, deviceIdList: ", deviceIdList);
    for (let i = 0; i < deviceIdList.length; i++) {
      //console.log("Doing polling for device: ",deviceIdList[i]);
      getMeas(deviceIdList[i]);
    }
    setTimeout(poll, 5000);
    }
    poll();
}

function switchShow(button) {
  //console.log("SWITCH SHOW CALLED");
  // Switch dropdown on click
  const dropdownContent = button.nextElementSibling;
  if (dropdownContent.classList.contains("show")) {
    dropdownContent.classList.remove("show");
  } else {
    dropdownContent.classList.toggle("show");
  }
}

window.onclick = function (event) {
  // Close dropdown on outside click
  if (
    !event.target.matches(".dropbtn") &&
    !event.target.matches(".dd-element") &&
    !event.target.matches(".dropdown-content")
  ) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains("show")) {
        openDropdown.classList.remove("show");
      }
    }
  }
};

// On page load
document.addEventListener("DOMContentLoaded", function () {
  getDevices();
});
