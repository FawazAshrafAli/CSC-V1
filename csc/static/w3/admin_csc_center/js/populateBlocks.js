$(document).ready(() => {
    $('#district-dropdown').on('change', function() {
        const districtId = $(this).val();
        const stateId = $('#state-dropdown').val();
        
        $.ajax({
            type: 'get',
            url: '/admin/get_blocks/',
            data: {
                'district_id': districtId,
                'state_id': stateId
            },
            dataType : 'json',
            success: data => {
                $('#block-dropdown').chosen('destroy');
                $('#block-dropdown').html(`<option label="Select Block"></option>`);
                if (data.blocks && Array.isArray(data.blocks)) {
                    data.blocks.forEach(block => {
                        let html = `<option value="${block.id}">${block.block}</option>`
                        $('#block-dropdown').append(html);
                    });
                } else {
                    $('#block-dropdown').html(`<option label="Select Block"></option>`);
                };
    
                $('#block-dropdown').chosen();
    
            },
            error: (jqXHR, textStatus, errorThrow) => {
                console.log('Error: ', textStatus, errorThrow);
            }
        });
    });
});