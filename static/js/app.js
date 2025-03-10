document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload validation
    const excelFileInput = document.getElementById('excel-file');
    const zipFileInput = document.getElementById('zip-file');
    const uploadForm = document.getElementById('upload-form');
    const searchForm = document.getElementById('search-form');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            if (!excelFileInput.files.length || !zipFileInput.files.length) {
                event.preventDefault();
                showAlert('Please select both Excel and ZIP files', 'danger');
            }
        });
    }
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            const studentId = document.getElementById('student-id').value.trim();
            if (!studentId) {
                event.preventDefault();
                showAlert('Please enter a Student ID', 'warning');
            }
        });
    }
    
    // File input label update
    if (excelFileInput) {
        excelFileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'Choose Excel file';
            document.getElementById('excel-file-label').textContent = fileName;
        });
    }
    
    if (zipFileInput) {
        zipFileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'Choose ZIP file';
            document.getElementById('zip-file-label').textContent = fileName;
        });
    }
    
    // Helper function to show alerts
    function showAlert(message, type) {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            const alertHtml = `
                <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
            alertContainer.innerHTML = alertHtml;
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const alert = document.querySelector('.alert');
                if (alert) {
                    bootstrap.Alert.getOrCreateInstance(alert).close();
                }
            }, 5000);
        }
    }
});
