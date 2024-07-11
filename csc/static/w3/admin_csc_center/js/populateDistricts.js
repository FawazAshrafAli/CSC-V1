$(document).ready(() => {
    $('#state-dropdown').on('change', function() {
        const stateId = $(this).val();
        
        $.ajax({
            type: 'get',
            url: '/admin/get_districts/',
            data: {'state_id': stateId},
            dataType : 'json',
            success: data => {
                $('#district-dropdown').chosen('destroy');
                $('#district-dropdown').html(`<option label="Select District"></option>`);
                if (data.districts && Array.isArray(data.districts)) {
                    data.districts.forEach(district => {
                        let html = `<option value="${district.id}">${district.district}</option>`
                        $('#district-dropdown').append(html);
                    });
                } else {
                    $('#district-dropdown').html(`<option label="Select District"></option>`);
                };
    
                $('#district-dropdown').chosen();
    
            },
            error: (jqXHR, textStatus, errorThrow) => {
                console.log('Error: ', textStatus, errorThrow);
            }
        });
    });
});