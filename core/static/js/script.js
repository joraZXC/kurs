document.addEventListener('DOMContentLoaded', function() {
         flatpickr('.datepicker', {
             dateFormat: 'Y-m-d',
         });
         $('.table').DataTable();
     });