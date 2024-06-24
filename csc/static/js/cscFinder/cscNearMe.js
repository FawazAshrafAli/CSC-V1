function cscNearMe() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);

                $.ajax({
                    data: 'GET',
                    url: '/locate_me/',
                    dataType: 'json',
                    data: {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    success: function (data) {
                        if (data.place) {
                            $('#place').html('Place: ' + `<span class='text-success'>${data.place}<span>`);
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
                })

            },
            (error) => {
                console.error(`Error: ${error.message}`);
            }
        );
    } else {
        console.error("Geolocation is not supported by this browser.");
    }

}