function populateDistricts(stateId) {
    $.ajax({
        type: 'get',
        url: '/admin/get_districts/',
        data: {'state_id': stateId},
        dataType : 'json',
        success: data => {
            $('#district-dropdown').chosen('destroy');

            if ($('#district-dropdown-input')) {
                $('#district-dropdown-input').html(`<option label="Select District"></option>`);
            }

            $('#district-dropdown').html(`<option label="Select District"></option>`);
            if (data.districts && Array.isArray(data.districts)) {
                data.districts.forEach(district => {
                    let html = `<option value="${district.id}">${district.district}</option>`

                    if ($('#district-dropdown-input')) {
                        $('#district-dropdown-input').append(html);    
                    }

                    $('#district-dropdown').append(html);
                });
            } else {
                if ($('#district-dropdown-input')) {
                    $('#district-dropdown-input').html(`<option label="Select District"></option>`);
                }

                $('#district-dropdown').html(`<option label="Select District"></option>`);
            };

            $('#district-dropdown').chosen();

        },
        error: (jqXHR, textStatus, errorThrow) => {
            console.log('Error: ', textStatus, errorThrow);
        }
    });
};

$(document).ready(() => {
    $('#state-dropdown').on('change', function() {
        const stateId = $(this).val();
        populateDistricts(stateId);        
    });
});