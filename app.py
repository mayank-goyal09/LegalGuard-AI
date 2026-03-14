"""
Contract Risk Intelligence v2.0 - Streamlit Web Application
Enhanced UI with 150+ pattern detection for small business contract analysis.
"""

import streamlit as st
import os
import tempfile
from datetime import datetime

# Must be first Streamlit command
st.set_page_config(
    page_title="Contract Risk Intelligence v2.0",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules
from src.extractor import ContractExtractor
from src.processor import ContractProcessor
from src.analyzer import RiskAnalyzer, RiskLevel, RiskCategory


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS STYLING - Premium Dark Theme with Glassmorphism
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Import Premium Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, rgba(26,26,46,0.9) 0%, rgba(22,33,62,0.9) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(78, 205, 196, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        color: #fff;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #4ECDC4, #44A08D, #6BB9F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    .main-header p {
        color: #a0aec0;
        font-size: 1.1rem;
    }
    
    .version-badge {
        display: inline-block;
        background: linear-gradient(90deg, #4ECDC4, #44A08D);
        color: #fff;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    /* Risk Score Card */
    .risk-card {
        background: linear-gradient(135deg, rgba(30,30,46,0.95) 0%, rgba(45,45,68,0.95) 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .risk-critical { 
        border-left: 5px solid #FF4757; 
        box-shadow: 0 0 20px rgba(255,71,87,0.3);
    }
    .risk-high { 
        border-left: 5px solid #FF6B35; 
        box-shadow: 0 0 20px rgba(255,107,53,0.3);
    }
    .risk-medium { 
        border-left: 5px solid #FFC048; 
        box-shadow: 0 0 20px rgba(255,192,72,0.3);
    }
    .risk-low { 
        border-left: 5px solid #2ED573; 
        box-shadow: 0 0 20px rgba(46,213,115,0.3);
    }
    .risk-none { 
        border-left: 5px solid #6c757d; 
    }
    
    /* Large Score Display */
    .score-display {
        font-size: 5rem;
        font-weight: 800;
        text-align: center;
        margin: 1.5rem 0;
        text-shadow: 0 0 30px currentColor;
    }
    
    .score-critical { color: #FF4757; }
    .score-high { color: #FF6B35; }
    .score-medium { color: #FFC048; }
    .score-low { color: #2ED573; }
    
    /* Finding Cards */
    .finding-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .finding-card:hover {
        transform: translateX(5px);
        background: rgba(255,255,255,0.06);
    }
    
    .finding-critical { border-left-color: #FF4757; background: rgba(255,71,87,0.08); }
    .finding-high { border-left-color: #FF6B35; background: rgba(255,107,53,0.08); }
    .finding-medium { border-left-color: #FFC048; background: rgba(255,192,72,0.08); }
    .finding-low { border-left-color: #2ED573; background: rgba(46,213,115,0.08); }
    
    /* Category Badge */
    .category-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(78, 205, 196, 0.2);
        color: #4ECDC4;
        margin-bottom: 0.5rem;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        background: rgba(255,255,255,0.06);
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4ECDC4, #44A08D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Category Progress Bars */
    .category-bar {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 12px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .category-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #4ECDC4, #44A08D);
        transition: width 0.5s ease;
    }
    
    /* Recommendation Box */
    .recommendation-box {
        background: rgba(45, 212, 191, 0.08);
        border: 1px solid rgba(45, 212, 191, 0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
    
    /* Upload Area */
    .upload-area {
        border: 2px dashed rgba(78, 205, 196, 0.4);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(78, 205, 196, 0.03);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #4ECDC4;
        background: rgba(78, 205, 196, 0.08);
    }
    
    /* Severity Counter */
    .severity-counter {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .counter-critical {
        background: rgba(255,71,87,0.2);
        color: #FF4757;
        border: 1px solid rgba(255,71,87,0.3);
    }
    .counter-high {
        background: rgba(255,107,53,0.2);
        color: #FF6B35;
        border: 1px solid rgba(255,107,53,0.3);
    }
    .counter-medium {
        background: rgba(255,192,72,0.2);
        color: #FFC048;
        border: 1px solid rgba(255,192,72,0.3);
    }
    .counter-low {
        background: rgba(46,213,115,0.2);
        color: #2ED573;
        border: 1px solid rgba(46,213,115,0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem;
        color: #6c757d;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 3rem;
        background: rgba(0,0,0,0.2);
        border-radius: 20px;
    }
    
    /* Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .pulse { animation: pulse 2s infinite; }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_risk_color(level: RiskLevel) -> tuple:
    """Get color scheme for risk level."""
    colors = {
        RiskLevel.CRITICAL: ("#FF4757", "critical"),
        RiskLevel.HIGH: ("#FF6B35", "high"),
        RiskLevel.MEDIUM: ("#FFC048", "medium"),
        RiskLevel.LOW: ("#2ED573", "low"),
        RiskLevel.NONE: ("#6c757d", "none"),
    }
    return colors.get(level, ("#6c757d", "none"))


def get_level_emoji(level: RiskLevel) -> str:
    """Get emoji for risk level."""
    emojis = {
        RiskLevel.CRITICAL: "🔴",
        RiskLevel.HIGH: "🟠",
        RiskLevel.MEDIUM: "🟡",
        RiskLevel.LOW: "🟢",
        RiskLevel.NONE: "⚪",
    }
    return emojis.get(level, "⚪")


def get_category_icon(category: RiskCategory) -> str:
    """Get icon for category."""
    icons = {
        RiskCategory.LIABILITY: "⚠️",
        RiskCategory.TERMINATION: "🚪",
        RiskCategory.PAYMENT: "💰",
        RiskCategory.IP: "🧠",
        RiskCategory.CONFIDENTIALITY: "🔒",
        RiskCategory.NON_COMPETE: "⛔",
        RiskCategory.DISPUTE: "⚖️",
        RiskCategory.COMPLIANCE: "📋",
        RiskCategory.AUTO_RENEWAL: "🔄",
        RiskCategory.DATA_PRIVACY: "🔐",
        RiskCategory.REMEDIES: "⚡",
        RiskCategory.SCOPE: "📐",
    }
    return icons.get(category, "📄")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Contract Risk Intelligence <span class="version-badge">v2.0 Enhanced</span></h1>
        <p>AI-powered contract analysis with 150+ risk patterns. Catches "Red Team" style evasive language.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Analysis Settings")
        
        use_ai = st.toggle("Enable AI Summary", value=True, 
                          help="Use AI to generate smart summaries")
        
        model_choice = st.selectbox(
            "AI Model",
            ["google/flan-t5-small", "google/flan-t5-base"],
            help="Larger models are more accurate but slower"
        )
        
        st.markdown("---")
        
        st.markdown("### 📊 Detection Capabilities")
        st.markdown("""
        <div style='font-size: 0.85rem; color: #a0aec0;'>
        ✅ <b>150+ Risk Patterns</b><br>
        ✅ <b>12 Risk Categories</b><br>
        ✅ <b>Synonym Detection</b><br>
        ✅ <b>Red Team Language</b><br>
        ✅ <b>Danger Phrase Combos</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🏷️ Categories Analyzed")
        
        categories_list = [
            "⚠️ Liability & Indemnification",
            "🚪 Termination & Exit",
            "💰 Payment & Financial",
            "🧠 Intellectual Property",
            "🔒 Confidentiality & NDA",
            "⛔ Non-Compete & Restrictions",
            "⚖️ Dispute Resolution",
            "📋 Regulatory & Compliance",
            "🔄 Auto-Renewal & Lock-in",
            "🔐 Data Privacy & Security",
            "⚡ Remedies & Enforcement",
            "📐 Scope & Definitions"
        ]
        
        for cat in categories_list:
            st.markdown(f"<small>{cat}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #6c757d; font-size: 0.75rem;'>
            <p>Built for Small Businesses</p>
            <p>🔒 Secure • ⚡ Fast • 🎯 Accurate</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📄 Upload Your Contract")
        
        uploaded_file = st.file_uploader(
            "Drop your contract PDF here",
            type=["pdf"],
            help="Supported format: PDF (max 10MB)"
        )
        
        # Demo mode option
        use_demo = st.checkbox("🎭 Use demo contract (Red Team NDA sample)", value=False)
    
    with col2:
        st.markdown("### 💡 What We Detect")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; font-size: 0.9rem;'>
        <b>🔴 Critical:</b> Unlimited liability, IP transfers, waived rights<br><br>
        <b>🟠 High:</b> One-sided termination, broad indemnification<br><br>
        <b>🟡 Medium:</b> Auto-renewal, audit rights, data sharing<br><br>
        <b>🟢 Low:</b> Standard clauses, jurisdiction
        </div>
        """, unsafe_allow_html=True)
    
    # Process contract
    if uploaded_file or use_demo:
        with st.spinner("🔍 Analyzing contract with 150+ risk patterns..."):
            try:
                # Get contract text
                if use_demo:
                    contract_text = get_demo_contract()
                    filename = "Red_Team_NDA_Demo.pdf"
                else:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Extract text
                    extractor = ContractExtractor(tmp_path)
                    contract_text = extractor.extract_text()
                    filename = uploaded_file.name
                    
                    # Cleanup
                    os.unlink(tmp_path)
                
                # Analyze
                analyzer = RiskAnalyzer(model_name=model_choice, use_ai=use_ai)
                report = analyzer.analyze_contract(contract_text)
                
                # Display results
                display_results(report, filename, contract_text)
                
            except Exception as e:
                st.error(f"❌ Error analyzing contract: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>⚠️ <strong>Disclaimer:</strong> This tool provides automated analysis only. 
        Always consult with a qualified attorney before signing any legal document.</p>
        <p style='margin-top: 1rem;'>© 2024 Contract Risk Intelligence v2.0 | Enhanced with 150+ Patterns | Designed for Small Businesses</p>
    </div>
    """, unsafe_allow_html=True)


def display_results(report, filename: str, contract_text: str):
    """Display analysis results in a beautiful format."""
    
    color, level_class = get_risk_color(report.overall_level)
    emoji = get_level_emoji(report.overall_level)
    
    st.markdown("---")
    
    # Count findings by severity
    critical_count = sum(1 for f in report.findings if f.level == RiskLevel.CRITICAL)
    high_count = sum(1 for f in report.findings if f.level == RiskLevel.HIGH)
    medium_count = sum(1 for f in report.findings if f.level == RiskLevel.MEDIUM)
    low_count = sum(1 for f in report.findings if f.level == RiskLevel.LOW)
    
    # Overall Risk Display
    st.markdown(f"""
    <div class="risk-card risk-{level_class}">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h2 style='color: #fff; margin: 0;'>📊 Analysis Complete</h2>
                <p style='color: #a0aec0; margin: 0.5rem 0;'>{filename}</p>
            </div>
            <div style='text-align: right;'>
                <div class="score-display score-{level_class}">{report.risk_percentage}%</div>
                <p style='color: {color}; font-weight: 700; font-size: 1.3rem;'>{emoji} {report.overall_level.name} RISK</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Severity Counters
    st.markdown(f"""
    <div style='text-align: center; margin: 1.5rem 0;'>
        <span class="severity-counter counter-critical">🔴 {critical_count} Critical</span>
        <span class="severity-counter counter-high">🟠 {high_count} High</span>
        <span class="severity-counter counter-medium">🟡 {medium_count} Medium</span>
        <span class="severity-counter counter-low">🟢 {low_count} Low</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Score", f"{report.total_score} pts", 
                 delta=f"of {report.max_possible_score} max")
    with col2:
        st.metric("Total Findings", len(report.findings),
                 delta=f"{critical_count + high_count} need action")
    with col3:
        categories_hit = len([c for c, v in report.category_breakdown.items() if v > 0])
        st.metric("Categories Affected", categories_hit,
                 delta=f"of 12 total")
    with col4:
        st.metric("Contract Length", f"{len(contract_text):,} chars",
                 delta=f"~{len(contract_text) // 500} pages")
    
    st.markdown("---")
    
    # Category Breakdown with Visual Bars
    st.markdown("### 📈 Risk by Category")
    
    # Get max score for scaling
    max_cat_score = max(report.category_breakdown.values()) if report.category_breakdown else 1
    
    cols = st.columns(2)
    sorted_categories = sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True)
    
    for idx, (cat, score) in enumerate(sorted_categories):
        if score > 0:
            with cols[idx % 2]:
                percentage = min(100, (score / max_cat_score) * 100)
                st.markdown(f"""
                <div style='margin: 0.8rem 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.3rem;'>
                        <span style='color: #fff; font-size: 0.9rem;'>{cat}</span>
                        <span style='color: #4ECDC4; font-weight: 600;'>{score} pts</span>
                    </div>
                    <div class="category-bar">
                        <div class="category-fill" style='width: {percentage}%;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Findings Tabs
    st.markdown("### 🔍 Detailed Findings")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🚨 Critical & High ({critical_count + high_count})", 
        f"🟡 Medium ({medium_count})",
        f"📋 All Findings ({len(report.findings)})", 
        "💡 Action Items"
    ])
    
    with tab1:
        critical_high = [f for f in report.findings if f.level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        
        if critical_high:
            for finding in critical_high:
                emoji = get_level_emoji(finding.level)
                color, level_class = get_risk_color(finding.level)
                cat_icon = get_category_icon(finding.category)
                
                with st.expander(f"{emoji} {cat_icon} {finding.category.value}: '{finding.phrase_matched[:50]}...'", expanded=(finding.level == RiskLevel.CRITICAL)):
                    st.markdown(f"**Risk Level:** {finding.level.name} ({finding.score_impact} points)")
                    st.markdown(f"**Matched Text:** `{finding.phrase_matched}`")
                    st.markdown(f"**Context:** _{finding.context[:300]}..._")
                    st.warning(f"**📌 Recommendation:** {finding.recommendation}")
        else:
            st.success("🎉 No critical or high-risk findings! Looking good.")
    
    with tab2:
        medium_findings = [f for f in report.findings if f.level == RiskLevel.MEDIUM]
        
        if medium_findings:
            # Group by category
            categories = {}
            for f in medium_findings:
                cat_name = f.category.value
                if cat_name not in categories:
                    categories[cat_name] = []
                categories[cat_name].append(f)
            
            for cat_name, findings in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
                with st.expander(f"📁 {cat_name} ({len(findings)} findings)"):
                    for f in findings:
                        st.markdown(f"- 🟡 **{f.phrase_matched[:60]}...** - {f.recommendation}")
        else:
            st.info("No medium-risk findings detected.")
    
    with tab3:
        if report.findings:
            # Summary by severity
            st.markdown("#### By Severity Level")
            
            for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]:
                level_findings = [f for f in report.findings if f.level == level]
                if level_findings:
                    emoji = get_level_emoji(level)
                    with st.expander(f"{emoji} {level.name} ({len(level_findings)} items)"):
                        for f in level_findings:
                            cat_icon = get_category_icon(f.category)
                            st.markdown(f"- {cat_icon} **[{f.category.value}]** {f.phrase_matched[:60]}...")
        else:
            st.info("No risk patterns detected. Manual review still recommended.")
    
    with tab4:
        st.markdown("#### ✅ Priority Action Items")
        st.markdown("_Address these in order of importance:_")
        
        for idx, rec in enumerate(report.recommendations[:10], 1):
            st.markdown(f"""
            <div class="recommendation-box">
                <strong>{idx}.</strong> {rec}
            </div>
            """, unsafe_allow_html=True)
        
        # AI Summary
        if report.summary:
            st.markdown("---")
            st.markdown("#### 🤖 AI Analysis Summary")
            st.info(report.summary)
    
    st.markdown("---")
    
    # Download Section
    st.markdown("### 📥 Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_text = generate_text_report(report, filename)
        st.download_button(
            label="📄 Download Full Report (TXT)",
            data=report_text,
            file_name=f"contract_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        report_md = generate_markdown_report(report, filename)
        st.download_button(
            label="📝 Download Report (Markdown)",
            data=report_md,
            file_name=f"contract_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )


def generate_text_report(report, filename: str) -> str:
    """Generate downloadable text report."""
    lines = [
        "=" * 70,
        "CONTRACT RISK INTELLIGENCE REPORT v2.0",
        "=" * 70,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"File: {filename}",
        "",
        f"OVERALL RISK: {report.overall_level.name}",
        f"Risk Score: {report.total_score} / {report.max_possible_score} ({report.risk_percentage}%)",
        "",
        "FINDING COUNTS:",
        f"  Critical: {sum(1 for f in report.findings if f.level == RiskLevel.CRITICAL)}",
        f"  High: {sum(1 for f in report.findings if f.level == RiskLevel.HIGH)}",
        f"  Medium: {sum(1 for f in report.findings if f.level == RiskLevel.MEDIUM)}",
        f"  Low: {sum(1 for f in report.findings if f.level == RiskLevel.LOW)}",
        f"  Total: {len(report.findings)}",
        "",
        "CATEGORY BREAKDOWN:",
        "-" * 50,
    ]
    
    for cat, score in sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            lines.append(f"  {cat}: {score} points")
    
    lines.extend([
        "",
        "KEY FINDINGS:",
        "-" * 50,
    ])
    
    for f in report.findings:
        lines.append(f"  [{f.level.name}] {f.category.value}: '{f.phrase_matched[:50]}...'")
        lines.append(f"    -> {f.recommendation}")
    
    lines.extend([
        "",
        "AI SUMMARY:",
        "-" * 50,
        f"  {report.summary}",
        "",
        "RECOMMENDATIONS:",
        "-" * 50,
    ])
    
    for i, rec in enumerate(report.recommendations, 1):
        lines.append(f"  {i}. {rec}")
    
    lines.extend([
        "",
        "=" * 70,
        "DISCLAIMER: This is an automated analysis. Always consult with",
        "a qualified attorney before signing any legal document.",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def generate_markdown_report(report, filename: str) -> str:
    """Generate downloadable markdown report."""
    critical = sum(1 for f in report.findings if f.level == RiskLevel.CRITICAL)
    high = sum(1 for f in report.findings if f.level == RiskLevel.HIGH)
    medium = sum(1 for f in report.findings if f.level == RiskLevel.MEDIUM)
    low = sum(1 for f in report.findings if f.level == RiskLevel.LOW)
    
    md = f"""# Contract Risk Intelligence Report v2.0

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File:** {filename}

---

## 🎯 Overall Risk: **{report.overall_level.name}**

| Metric | Value |
|--------|-------|
| Risk Score | {report.total_score} / {report.max_possible_score} |
| Risk Percentage | {report.risk_percentage}% |
| Critical Findings | {critical} |
| High Findings | {high} |
| Medium Findings | {medium} |
| Low Findings | {low} |
| **Total Findings** | **{len(report.findings)}** |

---

## 📊 Category Breakdown

| Category | Score |
|----------|-------|
"""
    
    for cat, score in sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            md += f"| {cat} | {score} pts |\n"
    
    md += "\n---\n\n## 🔍 Key Findings\n\n"
    
    for level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
        findings = [f for f in report.findings if f.level == level]
        if findings:
            md += f"### {level.name} Risk\n\n"
            for f in findings:
                md += f"- **[{f.category.value}]** `{f.phrase_matched[:50]}...`\n"
                md += f"  - Recommendation: {f.recommendation}\n\n"
    
    md += "---\n\n## ✅ Action Items\n\n"
    
    for i, rec in enumerate(report.recommendations[:10], 1):
        md += f"{i}. {rec}\n"
    
    md += f"""
---

## 🤖 AI Summary

{report.summary}

---

> ⚠️ **Disclaimer:** This is an automated analysis. Always consult with a qualified attorney before signing any legal document.
"""
    
    return md


def get_demo_contract() -> str:
    """Return demo Red Team NDA contract text for testing."""
    return """
    REDITEAM NDA VARIANT I — Derivative & Ownership Pressure
    
    This Non-Disclosure Agreement ("Agreement") is entered into between the Disclosing Party 
    and the Receiving Party for the purpose of evaluating a potential technical or business 
    relationship ("Purpose").
    
    1. Confidential Information. "Confidential Information" includes all information disclosed 
    directly or indirectly, whether tangible or intangible, fixed or unfixed, perceived or derived, 
    including analyses, notes, models, derivatives, recollections, and any information a reasonable 
    person might associate with the Disclosing Party's activities.
    
    2. Use Restriction. The Receiving Party shall not use Confidential Information for any purpose 
    except the Purpose, nor for any internal benchmarking, model training, competitive analysis, 
    or derivative development not expressly authorized in writing.
    
    3. Derivative Ownership. All derivatives, improvements, feedback, reconstructions, simulations, 
    and analytical outputs that incorporate or are informed by Confidential Information shall be 
    owned exclusively by the Disclosing Party.
    
    4. Security. The Receiving Party shall implement administrative, technical, physical, and 
    procedural controls sufficient to prevent any unauthorized access, inference, reconstruction, 
    or memorization of Confidential Information.
    
    5. Survival. Obligations under this Agreement shall survive termination and continue for so 
    long as the Confidential Information remains confidential, whether or not such status is 
    independently verifiable.
    
    6. Remedies. The Receiving Party agrees that any breach constitutes irreparable harm and 
    consents to injunctive, equitable, and specific performance remedies without bond, notice, 
    or proof of damages.
    
    7. Jurisdiction. The Disclosing Party may elect exclusive jurisdiction in any forum where 
    harm is reasonably alleged to have occurred.
    
    REDITEAM NDA VARIANT II — Scope Creep & Audit Control
    
    This Agreement governs all disclosures made before or after the effective date, whether or not 
    reduced to material form, that relate in any manner to the Disclosing Party's research, operations, 
    partners, or prospective activities.
    
    1. Scope Expansion. Confidential Information includes third-party data, inferred information, 
    metadata, behavioral observations, system outputs, and information retained unintentionally.
    
    2. Non-Circumvention. The Receiving Party shall not, directly or indirectly, pursue any opportunity, 
    collaboration, or development reasonably connected to the Confidential Information without the 
    Disclosing Party's prior written consent.
    
    3. Audit Rights. Upon reasonable notice, the Disclosing Party may audit systems, records, and 
    security practices of the Receiving Party to verify compliance, including access to relevant personnel.
    
    4. Return and Certification. Upon request, the Receiving Party shall destroy or return all 
    Confidential Information and certify in writing that no residual, latent, embedded, or archival 
    forms remain accessible.
    
    5. Liability Allocation. The Receiving Party assumes all liability arising from access to 
    Confidential Information, including claims brought by third parties, whether foreseeable or not.
    
    6. Continuity. Any successor, acquirer, or reorganized entity of the Receiving Party shall be 
    bound by obligations no less restrictive than those herein.
    
    REDITEAM NDA VARIANT III — Behavioral & Temporal Overreach
    
    This Agreement establishes minimum obligations and does not limit additional duties that may arise 
    from the nature, sensitivity, or strategic relevance of the Confidential Information.
    
    1. Behavioral Controls. The Receiving Party shall ensure that personnel with access to Confidential 
    Information do not engage in parallel research, training, or analytical activities that could 
    reasonably be construed as derivative.
    
    2. Information Gravity. Any knowledge that becomes inseparable from the Receiving Party's 
    operational processes shall nonetheless be treated as Confidential Information and remain subject 
    to restriction.
    
    3. Remedies Without Limitation. The Disclosing Party's remedies shall be cumulative and may be 
    pursued concurrently in law, equity, contract, or tort, without election or exhaustion.
    
    4. Indefinite Non-Disclosure. If Confidential Information cannot be conclusively demonstrated to 
    have entered the public domain, non-disclosure obligations shall be presumed ongoing.
    
    5. Interpretation. This Agreement shall be interpreted to afford maximum protection to Confidential 
    Information consistent with applicable law.
    """


if __name__ == "__main__":
    main()
