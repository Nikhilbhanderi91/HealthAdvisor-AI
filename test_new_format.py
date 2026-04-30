#!/usr/bin/env python3
"""
Test script to verify the new medical report format implementation.
Tests with the example case: Akshaybhai (Age 23)
Hb 9.6 → 🔴 LOW
MCV 101.7 → 🟡 HIGH
Platelets 44,000 → 🚨 CRITICAL LOW
WBC 3870 → 🔴 LOW
"""

from health_backend import (
    analyze_parameter_with_severity,
    generate_diagnosis,
    generate_interpretation,
    generate_advice,
    generate_formatted_report
)

# Test case: Akshaybhai (Age 23)
test_params = {
    'Hemoglobin': 9.6,
    'MCV': 101.7,
    'Platelets': 44000,
    'WBC': 3870
}

print("=" * 70)
print("TESTING NEW MEDICAL REPORT FORMAT")
print("=" * 70)
print("\nTest Case: Akshaybhai (Age 23)")
print("Expected: Severe Macrocytic Anemia + Low Immunity + Critical Platelet Count")
print("-" * 70)

# Analyze each parameter
results = []
for param, value in test_params.items():
    result = analyze_parameter_with_severity(param, value, gender='male')
    results.append(result)
    print(f"{param}: {value} → {result['status']} (Severity: {result['severity']})")

print("\n" + "=" * 70)
print("GENERATING DIAGNOSIS")
print("=" * 70)
diagnosis = generate_diagnosis(results)
print(f"Diagnosis: {diagnosis}")

print("\n" + "=" * 70)
print("GENERATING INTERPRETATION")
print("=" * 70)
interpretation = generate_interpretation(results, diagnosis)
print(f"Interpretation: {interpretation}")

print("\n" + "=" * 70)
print("GENERATING ADVICE")
print("=" * 70)
advice = generate_advice(results, diagnosis)
print(f"Advice: {advice}")

print("\n" + "=" * 70)
print("FULL FORMATTED REPORT")
print("=" * 70)
formatted_report = generate_formatted_report(
    results, 
    patient_name='Akshaybhai', 
    patient_age=23, 
    gender='male'
)
print(formatted_report)

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Verify expected outputs
expected_diagnosis_patterns = [
    'Macrocytic Anemia',
    'Low Immunity',
    'Critical'
]

diagnosis_match = any(pattern in diagnosis for pattern in expected_diagnosis_patterns)
print(f"✅ Diagnosis contains expected patterns: {diagnosis_match}")

# Check severity indicators
has_critical = any('🚨' in r['status'] for r in results)
has_high = any('🔴' in r['status'] for r in results)
has_slight = any('🟡' in r['status'] for r in results)

print(f"✅ Has 🚨 CRITICAL indicators: {has_critical}")
print(f"✅ Has 🔴 HIGH/LOW indicators: {has_high}")
print(f"✅ Has 🟡 SLIGHT indicators: {has_slight}")

# Check specific parameter statuses
hb_result = next(r for r in results if r['parameter'] == 'Hemoglobin')
mcv_result = next(r for r in results if r['parameter'] == 'MCV')
platelet_result = next(r for r in results if r['parameter'] == 'Platelets')
wbc_result = next(r for r in results if r['parameter'] == 'WBC')

print(f"\n✅ Hemoglobin 9.6 status: {hb_result['status']} (Expected: 🔴 LOW)")
print(f"✅ MCV 101.7 status: {mcv_result['status']} (Expected: 🟡 HIGH)")
print(f"✅ Platelets 44000 status: {platelet_result['status']} (Expected: 🚨 CRITICAL LOW)")
print(f"✅ WBC 3870 status: {wbc_result['status']} (Expected: 🔴 LOW)")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
