function filteredCscFinder () {
    var state = document.getElementById('state-dropdown').value
    var district = document.getElementById('district-dropdown').value
    var block = document.getElementById('block-dropdown').value

    $.ajax({
        data: 'GET',
        url: '/filtered_location/',
        dataType: 'json',
        data : {
            'state': state, 
            'district': district,
            'block': block
        },
        success: function (data) {
            if (data.block != null && data.block != '') {
                $('#place').html('Place: ' + data.block);
            } else {
                $('#place').html('');
            };

            $('#csc-centers').html('')
            if (data.centers_data && Array.isArray(data.centers_data)) {
                data.centers_data.forEach(function (center_data) {                    
                    var newRow = `<div class="card" style="">                    
                    <div class="card-body shadow">
                        <h5 class="card-title">${center_data.name}</h5>
                        <p class="card-text">CSC ID: ${center_data.csc_id}</p>
                        <p class="card-text">Phone: <a href="callto:${center_data.phone}">${center_data.phone}</a></p>
                        <p class="card-text">Alternative Number: <a href="callto:${center_data.alternative_number}">${center_data.alternative_number}</a></p>
                        <p class="card-text">Email: <a href="emailto:${center_data.email}">${center_data.email}</a></p>
                        <div class="text-center">
                            <a href="/csc/${center_data.csc_id}" class="btn btn-outline-primary px-5">View</a>
                        </div>
                    </div>
                </div>
                <br>`
                    $('#csc-centers').append(newRow)
                });
            } else {
                $('#csc-centers').html('')
            };

        },
        error: function (error) {
            console.error("Error: ", error);
        }                             
    });
}