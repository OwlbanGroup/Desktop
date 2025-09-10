import PayrollIntegration from './OSCAR-BROOME-REVENUE/payroll_integration.js';

// Define interfaces locally to match the expected structure
interface PayrollData {
  employeeId: string;
  salary: number;
  taxRate: number;
  deductions: number;
  bonuses: number;
  date: string;
  amount?: number;
}

interface PayrollEmployee {
  id: string;
  salary: number;
  taxRate: number;
  deductions: number;
  bonuses: number;
  accountNumber?: string;
  routingNumber?: string;
  name: string;
  department?: string;
  [key: string]: any;
}

interface PayrollResponse {
  success: boolean;
  message: string;
  data?: PayrollData | any;
}

interface TransactionStatus {
  success: boolean;
  status: string;
  message?: string;
}

interface ReconciliationResult {
  success: boolean;
  reconciledCount: number;
  message?: string;
}

// Test interface usage
const testPayrollData: PayrollData = {
  employeeId: 'EMP001',
  salary: 50000,
  taxRate: 0.25,
  deductions: 5000,
  bonuses: 2000,
  date: '2024-01-01',
  amount: 45000
};

const testEmployee: PayrollEmployee = {
  id: 'EMP001',
  salary: 50000,
  taxRate: 0.25,
  deductions: 5000,
  bonuses: 2000,
  accountNumber: '123456789',
  routingNumber: '021000021',
  name: 'John Doe',
  department: 'Engineering'
};

const testPayrollResponse: PayrollResponse = {
  success: true,
  message: 'Payroll processed successfully',
  data: testPayrollData
};

const testTransactionStatus: TransactionStatus = {
  success: true,
  status: 'completed',
  message: 'Transaction processed'
};

const testReconciliationResult: ReconciliationResult = {
  success: true,
  reconciledCount: 150,
  message: 'All transactions reconciled'
};

// Test class instantiation and method calls
const payrollIntegration = new PayrollIntegration('https://api.payroll.com', 'token123');

// Test employee payroll operations
payrollIntegration.addOrUpdateEmployeePayroll(testEmployee).then(addResult => {
  console.log('Add or update employee payroll result:', addResult);
});

payrollIntegration.getEmployeePayroll('EMP001').then(getResult => {
  console.log('Get employee payroll result:', getResult);
});

payrollIntegration.validateDirectDeposit(testEmployee).then(validateResult => {
  console.log('Validate direct deposit result:', validateResult);
});

payrollIntegration.getTransactionStatus('TXN001').then(statusResult => {
  console.log('Get transaction status result:', statusResult);
});

payrollIntegration.reconcileTransactions().then(reconcileResult => {
  console.log('Reconcile transactions result:', reconcileResult);
});

console.log('All type tests initiated successfully!');
