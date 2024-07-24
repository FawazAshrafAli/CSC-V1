
var districtBlocks = {
    "Palakkad (Palghat)": ["Alathur", "Attapadi", "Chittur", "Kollengode", "Kuzhalmannam", "Malampuzha", "Mannarkad", "Nemmara", "Ottappalam", "Palakkad", "Pattambi", "Sreekrishnapuram", "Trithala"]
};

function populateBlocks() {
    var districtDropdown = document.getElementById("district-dropdown");
    var blockDropdown = document.getElementById("block-dropdown");
    var selectedDistrict = districtDropdown.value;

    blockDropdown.innerHTML = "<option hidden disabled selected>Select Block</option>";

    if (selectedDistrict != 'Select District') {
        districtBlocks[selectedDistrict].forEach(function(block) {
            var option = document.createElement("option");
            option.text = block;
            blockDropdown.add(option);
        });
    };
};