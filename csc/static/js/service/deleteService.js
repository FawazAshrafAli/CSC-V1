function deleteService(serviceId) {
    $.ajax({
        data: 'GET',
        url: '/admin/get_service_details/' + serviceId,
        dataType: 'json',
        success: function (service) {
    
            if (service.name != null && service.name != '') {
                $('#deleting-service-object').html(service.name);
            } else {
                $('#deleting-service-object').html('');
            };
        },
        error: function (error) {
            console.error();
        },
    });
};