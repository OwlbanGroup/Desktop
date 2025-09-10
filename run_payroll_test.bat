@echo off
cd OSCAR-BROOME-REVENUE
npx ts-node ../test_payroll_integration_runner.ts > ../payroll_test_output.txt 2>&1
echo Test completed. Check payroll_test_output.txt for results.
