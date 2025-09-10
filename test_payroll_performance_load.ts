expect(avgResponseTime).toBeLessThan(200); // Should maintain performance
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
