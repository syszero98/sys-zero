// ==========================================
// STUDENT PANEL - JAVASCRIPT LOGIC
// ==========================================

class StudentPortal {
    constructor() {
        this.initElements();
        this.attachEventListeners();
        this.loadInitialData();
    }

    // Initialize DOM Elements
    initElements() {
        // Form Elements
        this.classSelect = document.getElementById('classSelect');
        this.yearSelect = document.getElementById('yearSelect');
        this.examSelect = document.getElementById('examSelect');
        this.searchInput = document.getElementById('searchInput');
        this.searchLabel = document.getElementById('searchLabel');
        this.searchBtn = document.getElementById('searchBtn');
        this.errorMsg = document.getElementById('errorMsg');
        this.adminGateway = document.getElementById('adminGateway');

        // Result Card Elements
        this.resultCard = document.getElementById('resultCard');
        this.closeResult = document.getElementById('closeResult');
        this.marksTableBody = document.getElementById('marksTableBody');
        this.studentName = document.getElementById('studentName');
        this.studentRoll = document.getElementById('studentRoll');
        this.studentClass = document.getElementById('studentClass');
        this.studentExam = document.getElementById('studentExam');
        this.printBtn = document.getElementById('printBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.searchAgainBtn = document.getElementById('searchAgainBtn');

        // Radio buttons
        this.searchTypeRadios = document.querySelectorAll('input[name="searchType"]');

        // Store all data
        this.allData = {};
        this.filteredData = {};
    }

    // Attach Event Listeners
    attachEventListeners() {
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.closeResult.addEventListener('click', () => this.closeResultCard());
        this.searchAgainBtn.addEventListener('click', () => this.closeResultCard());
        this.adminGateway.addEventListener('click', () => this.redirectToAdmin());
        
        // Dynamic dropdowns
        this.classSelect.addEventListener('change', () => this.updateYearDropdown());
        this.yearSelect.addEventListener('change', () => this.updateExamDropdown());

        // Search type toggle
        this.searchTypeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => this.updateSearchLabel(e.target.value));
        });

        // Print & Download
        this.printBtn.addEventListener('click', () => this.printMarksheet());
        this.downloadBtn.addEventListener('click', () => this.downloadPDF());

        // Enter key to search
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
    }

    // Load Initial Data
    async loadInitialData() {
        try {
            const response = await fetch('/api/get-options');
            const data = await response.json();

            if (data.success) {
                this.allData = data.data;
                this.populateClassDropdown();
            } else {
                this.showError('Failed to load data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Connection error. Please refresh the page.');
        }
    }

    // Populate Class Dropdown
    populateClassDropdown() {
        const classes = Object.keys(this.allData).sort();
        this.classSelect.innerHTML = '<option value="">-- Choose Class --</option>';
        
        classes.forEach(cls => {
            const option = document.createElement('option');
            option.value = cls;
            option.textContent = cls;
            this.classSelect.appendChild(option);
        });
    }

    // Update Year Dropdown (Dynamic)
    updateYearDropdown() {
        const selectedClass = this.classSelect.value;
        this.yearSelect.innerHTML = '<option value="">-- Choose Year --</option>';
        this.examSelect.innerHTML = '<option value="">-- Choose Exam --</option>';

        if (selectedClass && this.allData[selectedClass]) {
            const years = Object.keys(this.allData[selectedClass]).sort();
            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                this.yearSelect.appendChild(option);
            });
        }
    }

    // Update Exam Dropdown (Dynamic)
    updateExamDropdown() {
        const selectedClass = this.classSelect.value;
        const selectedYear = this.yearSelect.value;
        this.examSelect.innerHTML = '<option value="">-- Choose Exam --</option>';

        if (selectedClass && selectedYear && this.allData[selectedClass][selectedYear]) {
            const exams = Object.keys(this.allData[selectedClass][selectedYear]).sort();
            exams.forEach(exam => {
                const option = document.createElement('option');
                option.value = exam;
                option.textContent = exam;
                this.examSelect.appendChild(option);
            });

            // Store filtered data for search
            this.filteredData = this.allData[selectedClass][selectedYear];
        }
    }

    // Update Search Label
    updateSearchLabel(type) {
        if (type === 'roll') {
            this.searchLabel.textContent = 'Enter Roll Number *';
            this.searchInput.placeholder = 'Enter Roll Number';
        } else {
            this.searchLabel.textContent = 'Enter Student Name *';
            this.searchInput.placeholder = 'Enter Student Name';
        }
        this.searchInput.value = '';
        this.clearError();
    }

    // Handle Search
    async handleSearch() {
        const selectedClass = this.classSelect.value;
        const selectedYear = this.yearSelect.value;
        const selectedExam = this.examSelect.value;
        const searchType = document.querySelector('input[name="searchType"]:checked').value;
        const searchValue = this.searchInput.value.trim();

        // Validation
        if (!selectedClass || !selectedYear || !selectedExam || !searchValue) {
            this.showError('Please fill all fields');
            return;
        }

        try {
            const response = await fetch('/search-result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    class: selectedClass,
                    year: selectedYear,
                    exam: selectedExam,
                    searchType: searchType,
                    searchValue: searchValue
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayResult(result.data, selectedClass, selectedExam);
                this.clearError();
            } else {
                this.showError(result.message || 'Student not found');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Error searching. Please try again.');
        }
    }

    // Display Result
    displayResult(data, selectedClass, selectedExam) {
        // Update student info
        this.studentName.textContent = data.name || '-';
        this.studentRoll.textContent = data.roll || '-';
        this.studentClass.textContent = selectedClass;
        this.studentExam.textContent = selectedExam;

        // Clear and populate marks table
        this.marksTableBody.innerHTML = '';

        if (data.subjects && Array.isArray(data.subjects)) {
            data.subjects.forEach(subject => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${subject.name || '-'}</td>
                    <td>${subject.marks || '-'}</td>
                    <td>${subject.grade || '-'}</td>
                `;
                this.marksTableBody.appendChild(row);
            });
        }

        // Show result card
        this.resultCard.style.display = 'block';
        this.resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Close Result Card
    closeResultCard() {
        this.resultCard.style.display = 'none';
        this.searchInput.value = '';
        this.clearError();
    }

    // Print Marksheet
    printMarksheet() {
        const printWindow = window.open('', '', 'height=600,width=800');
        const content = this.resultCard.innerHTML;
        
        printWindow.document.write(`
            <html>
            <head>
                <title>Marksheet - ${this.studentName.textContent}</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .result-header { text-align: center; margin-bottom: 30px; }
                    .student-info { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }
                    .info-item { padding: 10px; border: 1px solid #ddd; }
                    .marks-table { width: 100%; border-collapse: collapse; }
                    .marks-table th, .marks-table td { border: 1px solid #ddd; padding: 10px; text-align: left; }
                    .marks-table th { background-color: #f0f0f0; }
                </style>
            </head>
            <body>
                <div class="result-header">
                    <h2>📊 Marksheet</h2>
                </div>
                ${content}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    // Download PDF
    downloadPDF() {
        alert('PDF download feature coming soon!\n\nFor now, use Print option to save as PDF.');
    }

    // Redirect to Admin Panel
    redirectToAdmin() {
        window.location.href = '/admin';
    }

    // Show Error
    showError(message) {
        this.errorMsg.textContent = message;
        this.errorMsg.classList.add('show');
    }

    // Clear Error
    clearError() {
        this.errorMsg.textContent = '';
        this.errorMsg.classList.remove('show');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new StudentPortal();
});
