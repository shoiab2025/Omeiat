$(document).ready(function() {
    // When any of the filter changes, update the form and submit it
    $('#jobFilterForm select, #jobFilterForm input[type="checkbox"], #jobFilterForm input[type="text"]').on('change', function() {
        $('#jobFilterForm').submit();
    });
});
