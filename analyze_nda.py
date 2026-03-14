"""
Enhanced NDA Analysis v2.0 - Compare with Claude's findings
"""

from src.extractor import ContractExtractor
from src.analyzer import RiskAnalyzer, RiskLevel, RiskCategory

# Extract
ext = ContractExtractor('Red_Team_NDA_Pack.pdf')
text = ext.extract_text()

# Analyze with enhanced model
analyzer = RiskAnalyzer(model_name='google/flan-t5-small', use_ai=True)
report = analyzer.analyze_contract(text)

# Write comprehensive results
with open('NDA_ANALYSIS_V2_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('='*70 + '\n')
    f.write('CONTRACT RISK INTELLIGENCE v2.0 - ENHANCED ANALYSIS\n')
    f.write('File: Red_Team_NDA_Pack.pdf\n')
    f.write('='*70 + '\n\n')
    
    f.write(f'[EXTRACTION] Extracted {len(text):,} characters\n\n')
    
    f.write('='*70 + '\n')
    f.write('RISK ANALYSIS RESULTS\n')
    f.write('='*70 + '\n\n')
    
    f.write(f'OVERALL RISK: {report.overall_level.name}\n')
    f.write(f'Risk Score: {report.total_score} / {report.max_possible_score} ({report.risk_percentage}%)\n\n')
    
    # Count by severity
    critical_count = sum(1 for f in report.findings if f.level == RiskLevel.CRITICAL)
    high_count = sum(1 for f in report.findings if f.level == RiskLevel.HIGH)
    medium_count = sum(1 for f in report.findings if f.level == RiskLevel.MEDIUM)
    low_count = sum(1 for f in report.findings if f.level == RiskLevel.LOW)
    
    f.write('[FINDING COUNTS]\n')
    f.write('-'*50 + '\n')
    f.write(f'  CRITICAL: {critical_count}\n')
    f.write(f'  HIGH:     {high_count}\n')
    f.write(f'  MEDIUM:   {medium_count}\n')
    f.write(f'  LOW:      {low_count}\n')
    f.write(f'  TOTAL:    {len(report.findings)}\n\n')
    
    f.write('[CATEGORY BREAKDOWN]\n')
    f.write('-'*50 + '\n')
    for cat, score in sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            bar = '#' * min(30, score // 3)
            f.write(f'  {cat[:40]:<40} {score:>3} pts {bar}\n')
    
    f.write('\n[ALL FINDINGS - DETAILED]\n')
    f.write('='*70 + '\n')
    
    # Group by severity
    for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]:
        findings = [fi for fi in report.findings if fi.level == level]
        if findings:
            f.write(f'\n{"="*30} {level.name} RISK ({len(findings)} items) {"="*30}\n')
            for i, fi in enumerate(findings, 1):
                f.write(f'\n{i}. [{fi.category.value}]\n')
                f.write(f'   Matched: "{fi.phrase_matched}"\n')
                f.write(f'   Score: {fi.score_impact} points\n')
                f.write(f'   >> {fi.recommendation}\n')
    
    f.write('\n\n[AI SUMMARY]\n')
    f.write('-'*50 + '\n')
    f.write(f'{report.summary}\n')
    
    f.write('\n[TOP ACTION ITEMS]\n')
    f.write('-'*50 + '\n')
    for i, rec in enumerate(report.recommendations, 1):
        f.write(f'{i}. {rec}\n')
    
    f.write('\n' + '='*70 + '\n')
    f.write('COMPARISON WITH CLAUDE ANALYSIS:\n')
    f.write('='*70 + '\n')
    f.write(f'\nModel v2.0 Score: {report.total_score} points ({report.risk_percentage}%)\n')
    f.write(f'Claude Estimated: ~120 points (~24%)\n')
    f.write(f'Match Rate: {min(100, round(report.total_score / 120 * 100))}%\n')
    f.write('\n' + '='*70 + '\n')
    f.write('DISCLAIMER: Automated analysis - consult attorney before signing\n')
    f.write('='*70 + '\n')

print('='*70)
print('ENHANCED ANALYSIS v2.0 COMPLETE')
print('='*70)
print(f'\nOVERALL RISK: {report.overall_level.name}')
print(f'Risk Score: {report.total_score} / {report.max_possible_score} ({report.risk_percentage}%)')
print(f'\nFindings: {critical_count} CRITICAL, {high_count} HIGH, {medium_count} MEDIUM, {low_count} LOW')
print(f'Total: {len(report.findings)} findings')
print(f'\nComparison with Claude: {min(100, round(report.total_score / 120 * 100))}% match')
print('\nFull report saved to: NDA_ANALYSIS_V2_REPORT.txt')
