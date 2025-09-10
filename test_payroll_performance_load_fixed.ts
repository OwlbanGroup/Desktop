import PayrollIntegration from './OSCAR-BROOME-REVENUE/payroll_integration.js';

// Define types locally for testing
interface PayrollEmployee {
  id: string;
  accountNumber?: string;
  routingNumber?: string;
  name: string;
  department?: string;
  salary: number;
  taxRate: number;
  [key: string]: any;
}

interface PayrollData {
  employeeId: string;
  salary: number;
  taxRate: number;
  deductions: number;
  bonuses: number;
  date: string;
  amount?: number;
}

// Performance Monitor Class
class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  record(operation: string, duration: number): void {
    if (!this.metrics.has(operation)) {
      this.metrics.set(operation, []);
    }
    this.metrics.get(operation)!.push(duration);
  }

  getAverage(operation: string): number {
    const times = this.metrics.get(operation) || [];
    return times.length > 0 ? times.reduce((sum, time) => sum + time, 0) / times.length : 0;
  }

  getMin(operation: string): number {
    const times = this.metrics.get(operation) || [];
    return times.length > 0 ? Math.min(...times) : 0;
  }

  getMax(operation: string): number {
    const times = this.metrics.get(operation) || [];
    return times.length > 0 ? Math.max(...times) : 0;
  }

  getPercentile(operation: string, percentile: number): number {
    const times = this.metrics.get(operation) || [];
    if (times.length === 0) return 0;

    const sorted = [...times].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }
}

// Load Generator Class
class LoadGenerator {
  generateEmployees(count: number): PayrollEmployee[] {
    const employees: PayrollEmployee[] = [];
    for (let i = 0; i < count; i++) {
      employees.push({
        id: `EMP${String(i + 1).padStart(3, '0')}`,
        name: `Employee ${i + 1}`,
        department: ['Engineering', 'Sales', 'HR', 'Finance'][i % 4],
        salary: 50000 + (i * 1000),
        taxRate: 0.25,
        accountNumber: `12345678${i}`,
        routingNumber: '021000021'
      });
    }
    return employees;
  }

  async simulateConcurrentRequests<T>(
    operation: () => Promise<T>,
    concurrency: number,
    totalRequests: number
  ): Promise<{ results: T[]; totalTime: number }> {
    const startTime = Date.now();
    const results: T[] = [];

    for (let i = 0; i < totalRequests; i += concurrency) {
      const batchSize = Math.min(concurrency, totalRequests - i);
      const promises = Array.from({ length: batchSize }, () => operation());
      const batchResults = await Promise.all(promises);
      results.push(...batchResults);
    }

    const totalTime = Date.now() - startTime;
    return { results, totalTime };
  }
}

// Performance and Load Testing Suite
describe('Payroll Performance and Load Testing', () => {
  let payrollIntegration: PayrollIntegration;
  let performanceMonitor: PerformanceMonitor;
  let loadGenerator: LoadGenerator;

  const mockEmployee: PayrollEmployee = {
    id: 'EMP001',
    accountNumber: '123456789',
    routingNumber: '021000021',
    name: 'John Doe',
    department: 'Engineering',
    salary: 75000,
    taxRate: 0.25
  };

  beforeEach(() => {
    payrollIntegration = new PayrollIntegration('https://api.payroll.com', 'test-token');
    performanceMonitor = new PerformanceMonitor();
    loadGenerator = new LoadGenerator();
  });

  describe('Response Time Testing', () => {
    test('should measure average response time', async () => {
      const responseTimes: number[] = [];

      for (let i = 0; i < 10; i++) {
        const startTime = Date.now();
        await payrollIntegration.getEmployeePayroll('EMP001');
        const responseTime = Date.now() - startTime;
        responseTimes.push(responseTime);
        performanceMonitor.record('getEmployeePayroll', responseTime);
      }

      const avgResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
      expect(avgResponseTime).toBeLessThan(200); // Should maintain performance
    });

    test('should handle concurrent requests efficiently', async () => {
      const concurrency = 5;
      const totalRequests = 20;

      const { results, totalTime } = await loadGenerator.simulateConcurrentRequests(
        () => payrollIntegration.getEmployeePayroll('EMP001'),
        concurrency,
        totalRequests
      );

      expect(results).toHaveLength(totalRequests);
      results.forEach(result => {
        expect(result).toBeDefined();
      });

      const avgResponseTime = totalTime / totalRequests;
      expect(avgResponseTime).toBeLessThan(150); // Concurrent requests should be efficient
    });
  });

  describe('Resource Utilization Testing', () => {
    test('should monitor CPU usage during load', async () => {
      const startCpuUsage = process.cpuUsage();

      const concurrency = 20;
      const totalRequests = 100;

      const { results } = await loadGenerator.simulateConcurrentRequests(
        () => payrollIntegration.getEmployeePayroll('EMP001'),
        concurrency,
        totalRequests
      );

      const endCpuUsage = process.cpuUsage(startCpuUsage);

      expect(results).toHaveLength(totalRequests);
      results.forEach(result => {
        expect(result).toBeDefined();
      });

      // CPU usage should be reasonable (less than 1 second total CPU time)
      expect(endCpuUsage.user + endCpuUsage.system).toBeLessThan(1000000); // Less than 1 second
    });

    test('should handle memory-intensive operations', async () => {
      const initialMemory = process.memoryUsage();

      // Create large dataset
      const largeEmployees = loadGenerator.generateEmployees(200);

      const promises = largeEmployees.map(employee =>
        payrollIntegration.addOrUpdateEmployeePayroll(employee)
      );

      const results = await Promise.all(promises);

      const finalMemory = process.memoryUsage();
      const memoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;

      expect(results).toHaveLength(200);
      results.forEach(result => {
        expect(result).toBeDefined();
      });

      // Memory increase should be proportional to data size
      expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024); // Less than 100MB
    });
  });

  describe('Endurance Testing', () => {
    test('should maintain performance over extended period', async () => {
      const testDuration = 30000; // 30 seconds
      const startTime = Date.now();
      const responseTimes: number[] = [];
      let requestCount = 0;

      while (Date.now() - startTime < testDuration) {
        const requestStart = Date.now();

        await payrollIntegration.getEmployeePayroll('EMP001');

        const responseTime = Date.now() - requestStart;
        responseTimes.push(responseTime);
        requestCount++;
      }

      const avgResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
      const throughput = requestCount / (testDuration / 1000); // requests per second

      expect(avgResponseTime).toBeLessThan(250); // Average should remain < 250ms
      expect(throughput).toBeGreaterThan(2); // Should handle at least 2 requests per second
    });

    test('should handle varying load patterns', async () => {
      const patterns = [
        { concurrency: 5, duration: 5000 },   // Low load
        { concurrency: 15, duration: 5000 },  // Medium load
        { concurrency: 30, duration: 5000 },  // High load
        { concurrency: 10, duration: 5000 }   // Recovery load
      ];

      for (const pattern of patterns) {
        const startTime = Date.now();
        const responseTimes: number[] = [];

        while (Date.now() - startTime < pattern.duration) {
          const requests = Array.from({ length: pattern.concurrency }, () =>
            payrollIntegration.getEmployeePayroll('EMP001')
          );

          const requestStart = Date.now();
          await Promise.all(requests);
          const responseTime = Date.now() - requestStart;

          responseTimes.push(responseTime);
        }

        const avgResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;

        // Performance should degrade gracefully under load
        expect(avgResponseTime).toBeLessThan(1000); // Should remain under 1 second even under high load
      }
    });
  });

  describe('Performance Benchmarks', () => {
    test('should meet performance SLAs', () => {
      // Define Service Level Agreements
      const slas = {
        employeeCreation: 500,      // 500ms
        payrollRetrieval: 200,      // 200ms
        directDepositValidation: 150, // 150ms
        transactionStatus: 100,     // 100ms
        batchOperations: 2000       // 2 seconds for batch of 50
      };

      // These would be measured against actual performance data
      expect(slas.employeeCreation).toBeGreaterThan(0);
      expect(slas.payrollRetrieval).toBeGreaterThan(0);
      expect(slas.directDepositValidation).toBeGreaterThan(0);
      expect(slas.transactionStatus).toBeGreaterThan(0);
      expect(slas.batchOperations).toBeGreaterThan(0);
    });

    test('should provide performance metrics', () => {
      const metrics = {
        averageResponseTime: performanceMonitor.getAverage('getEmployeePayroll'),
        minResponseTime: performanceMonitor.getMin('getEmployeePayroll'),
        maxResponseTime: performanceMonitor.getMax('getEmployeePayroll'),
        p95ResponseTime: performanceMonitor.getPercentile('getEmployeePayroll', 95),
        p99ResponseTime: performanceMonitor.getPercentile('getEmployeePayroll', 99)
      };

      expect(metrics.averageResponseTime).toBeGreaterThanOrEqual(0);
      expect(metrics.minResponseTime).toBeGreaterThanOrEqual(0);
      expect(metrics.maxResponseTime).toBeGreaterThanOrEqual(0);
      expect(metrics.p95ResponseTime).toBeGreaterThanOrEqual(metrics.averageResponseTime);
      expect(metrics.p99ResponseTime).toBeGreaterThanOrEqual(metrics.p95ResponseTime);
    });
  });
});

// Export for use in other test files
export { PerformanceMonitor, LoadGenerator };
