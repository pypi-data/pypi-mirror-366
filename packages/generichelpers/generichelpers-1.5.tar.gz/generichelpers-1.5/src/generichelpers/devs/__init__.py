# Salary info extraction keys
PAYSLIP_COMPONENTS = {
    'company_name': [],
    'company_address': [],
    'month_info': [(
        'Pay slip',
        'Payslip',
        'Salary',
        'Salary Slip',
        'Salary info',
        'SalarySlip'
    )],
    'employee_info': [(
        'Emp Code',
        'Emp Name',
        'Emp Number',
        'Employee Code',
        'Employee Name',
        'Employee Number'
    )],
    'designation_info': ['Designation'],
    'pay_elements': ['Basic', ('Note', 'Net', '__')],
    'additional_info': ['Note', '__']
}
