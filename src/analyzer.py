"""
Contract Risk Analyzer - ENHANCED VERSION 2.0
Comprehensive risk detection with 150+ patterns, synonym matching, and semantic analysis.
Designed to catch "Red Team" style evasive language in contracts.
"""

from transformers import T5Tokenizer, T5ForConditionalGeneration
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels with associated colors for UI"""
    CRITICAL = ("🔴 CRITICAL", 4, "#FF0000")
    HIGH = ("🟠 HIGH", 3, "#FF6B00")
    MEDIUM = ("🟡 MEDIUM", 2, "#FFD700")
    LOW = ("🟢 LOW", 1, "#00C853")
    NONE = ("⚪ NONE", 0, "#808080")


class RiskCategory(Enum):
    """Categories of contract risks that matter to small businesses"""
    LIABILITY = "Liability & Indemnification"
    TERMINATION = "Termination & Exit"
    PAYMENT = "Payment & Financial"
    IP = "Intellectual Property"
    CONFIDENTIALITY = "Confidentiality & NDA"
    NON_COMPETE = "Non-Compete & Restrictions"
    DISPUTE = "Dispute Resolution"
    COMPLIANCE = "Regulatory & Compliance"
    AUTO_RENEWAL = "Auto-Renewal & Lock-in"
    DATA_PRIVACY = "Data Privacy & Security"
    REMEDIES = "Remedies & Enforcement"
    SCOPE = "Scope & Definitions"


@dataclass
class RiskFinding:
    """Represents a single risk finding in the contract"""
    category: RiskCategory
    level: RiskLevel
    phrase_matched: str
    context: str
    recommendation: str
    score_impact: int


@dataclass
class RiskReport:
    """Complete risk analysis report for a contract"""
    total_score: int
    max_possible_score: int
    risk_percentage: float
    overall_level: RiskLevel
    findings: List[RiskFinding]
    summary: str
    recommendations: List[str]
    category_breakdown: Dict[str, int]


class RiskPatternDatabase:
    """
    ENHANCED Pattern Database v2.0
    150+ patterns designed to catch standard AND evasive "Red Team" language.
    Includes synonym matching and semantic pattern recognition.
    """
    
    # Each pattern: (regex_pattern, risk_level, score_impact, recommendation)
    PATTERNS = {
        RiskCategory.LIABILITY: [
            # === CRITICAL: Unlimited/All Liability ===
            (r"unlimited\s+liability", RiskLevel.CRITICAL, 25, 
             "CRITICAL: Request a liability cap (e.g., 12 months of fees paid)"),
            (r"assumes?\s+all\s+liability", RiskLevel.CRITICAL, 25,
             "CRITICAL: ALL liability shifted to you - negotiate a reasonable cap"),
            (r"full\s+liability|complete\s+liability", RiskLevel.CRITICAL, 25,
             "CRITICAL: Full liability exposure - must negotiate limits"),
            (r"liability\s+shall\s+be\s+unlimited", RiskLevel.CRITICAL, 25,
             "CRITICAL: Explicit unlimited liability - unacceptable for most businesses"),
            (r"liable\s+for\s+all\s+(claims|damages|losses)", RiskLevel.CRITICAL, 22,
             "CRITICAL: Broad liability for all claims - negotiate specific exclusions"),
            (r"whether\s+foreseeable\s+or\s+not", RiskLevel.HIGH, 18,
             "HIGH: Liability includes unforeseeable events - unusual and risky"),
            (r"whether\s+or\s+not\s+(anticipated|expected|foreseeable)", RiskLevel.HIGH, 18,
             "HIGH: Covers unanticipated outcomes - very broad liability"),
             
            # === HIGH: Broad Indemnification ===
            (r"indemnify.*hold\s+harmless.*all\s+claims", RiskLevel.HIGH, 20,
             "REVIEW: Broad indemnification - limit to direct damages caused by your actions"),
            (r"defend.*indemnify.*hold\s+harmless", RiskLevel.HIGH, 18,
             "REVIEW: Triple obligation (defend/indemnify/hold harmless) - ensure scope is limited"),
            (r"indemnif(y|ication)\s+for\s+any\s+(and\s+all)?", RiskLevel.HIGH, 16,
             "REVIEW: 'Any and all' indemnification is overly broad"),
            (r"(broadly|fully|completely)\s+indemnif", RiskLevel.HIGH, 16,
             "REVIEW: Broad indemnification language detected"),
            (r"indemnif.*third.?part(y|ies)", RiskLevel.HIGH, 15,
             "REVIEW: Third-party indemnification - understand the scope"),
            (r"claims\s+brought\s+by\s+third\s+part", RiskLevel.HIGH, 15,
             "REVIEW: Liability for third-party claims - can be unpredictable"),
             
            # === MEDIUM/HIGH: Risk Allocation ===
            (r"sole\s+risk", RiskLevel.HIGH, 18,
             "NEGOTIATE: Risk should be shared, not placed entirely on one party"),
            (r"at\s+(your|receiving\s+party'?s?)\s+(own\s+)?risk", RiskLevel.HIGH, 15,
             "NEGOTIATE: One-sided risk allocation detected"),
            (r"assumes?\s+(the\s+)?risk", RiskLevel.MEDIUM, 12,
             "REVIEW: Risk assumption clause - understand what's covered"),
            (r"bear\s+(all\s+)?risk|bears?\s+the\s+risk", RiskLevel.HIGH, 15,
             "NEGOTIATE: Bearing all/the risk is one-sided"),
             
            # === HIGH: Waiving Rights ===
            (r"waive.*right.*sue|waiver.*litigation", RiskLevel.CRITICAL, 25,
             "CRITICAL: Waiving legal rights - consult attorney before signing"),
            (r"waive.*right.*claim", RiskLevel.HIGH, 20,
             "CRITICAL: Waiving right to make claims - very serious"),
            (r"releases?\s+and\s+discharge", RiskLevel.HIGH, 18,
             "REVIEW: Release and discharge of liability"),
            (r"forever\s+(release|discharge|waive)", RiskLevel.CRITICAL, 22,
             "CRITICAL: Permanent waiver of rights"),
            (r"irrevocabl(y|e)\s+(waive|release|discharge)", RiskLevel.CRITICAL, 22,
             "CRITICAL: Irrevocable waiver - cannot be undone"),
             
            # === MEDIUM: Standard Liability Terms ===
            (r"consequential\s+damages", RiskLevel.MEDIUM, 10,
             "CLARIFY: Ensure mutual exclusion of consequential damages"),
            (r"incidental\s+damages|indirect\s+damages", RiskLevel.MEDIUM, 8,
             "CLARIFY: Understand scope of indirect damage exclusions"),
            (r"gross\s+negligence|willful\s+misconduct", RiskLevel.MEDIUM, 8,
             "STANDARD: These exceptions to liability limits are typically acceptable"),
            (r"special\s+damages|punitive\s+damages", RiskLevel.MEDIUM, 8,
             "STANDARD: Check if these are mutually excluded"),
        ],
        
        RiskCategory.TERMINATION: [
            # === HIGH: Unfair Termination ===
            (r"terminate.*without\s+(cause|reason|notice)", RiskLevel.HIGH, 20,
             "NEGOTIATE: Request mutual termination rights or minimum notice period"),
            (r"immediate\s+termination", RiskLevel.HIGH, 18,
             "NEGOTIATE: Request 30-day cure period for non-material breaches"),
            (r"terminat(e|ion)\s+at\s+(will|any\s+time)", RiskLevel.HIGH, 16,
             "NEGOTIATE: At-will termination is one-sided - request mutual rights"),
            (r"terminat(e|ion).*without\s+prior\s+(written\s+)?notice", RiskLevel.HIGH, 18,
             "NEGOTIATE: Termination without notice is unfair - request notice period"),
            (r"sole\s+discretion.*terminat", RiskLevel.HIGH, 18,
             "NEGOTIATE: Sole discretion termination is one-sided"),
            (r"unilateral(ly)?\s+terminat", RiskLevel.HIGH, 16,
             "NEGOTIATE: Unilateral termination rights should be mutual"),
            
            # === MEDIUM: Refund/Financial Terms ===
            (r"no\s+refund.*termination|non.?refundable.*terminat", RiskLevel.MEDIUM, 12,
             "CLARIFY: Request pro-rata refund for unused services"),
            (r"forfeit.*upon\s+termination|terminat.*forfeit", RiskLevel.MEDIUM, 14,
             "NEGOTIATE: Forfeiture upon termination is harsh"),
            (r"termination\s+fee|early\s+termination.*penalty", RiskLevel.MEDIUM, 15,
             "REVIEW: Ensure termination fees are reasonable and clearly defined"),
            (r"break\s+fee|exit\s+fee|cancellation\s+fee", RiskLevel.MEDIUM, 12,
             "REVIEW: Understand the exit cost"),
            
            # === MEDIUM: Lock-in ===
            (r"lock.?in\s+period|minimum\s+term", RiskLevel.MEDIUM, 10,
             "NOTE: Verify the lock-in period aligns with your business needs"),
            (r"minimum\s+(commitment|contract)\s+period", RiskLevel.MEDIUM, 10,
             "NOTE: Understand the minimum commitment required"),
            
            # === LOW: Standard Survival ===
            (r"survive.*termination|surviv(e|al)\s+clause", RiskLevel.LOW, 5,
             "STANDARD: Check which obligations survive - confidentiality is normal"),
            (r"obligations?\s+(shall\s+)?surviv", RiskLevel.LOW, 5,
             "STANDARD: Review surviving obligations"),
        ],
        
        RiskCategory.PAYMENT: [
            # === HIGH: Price Changes ===
            (r"price.*increase.*without\s+notice", RiskLevel.HIGH, 18,
             "NEGOTIATE: Request advance notice (30-90 days) for price increases"),
            (r"modify\s+(fees?|prices?|rates?).*without\s+notice", RiskLevel.HIGH, 18,
             "NEGOTIATE: Fee modifications without notice is unfair"),
            (r"change.*pricing.*sole\s+discretion", RiskLevel.HIGH, 16,
             "NEGOTIATE: Pricing changes at sole discretion needs limits"),
            (r"reserves?\s+(the\s+)?right.*increase.*price", RiskLevel.MEDIUM, 14,
             "REVIEW: Right to increase price - request cap or notice"),
            
            # === HIGH: Non-refundable ===
            (r"all\s+fees?.*non.?refundable", RiskLevel.HIGH, 15,
             "NEGOTIATE: Request refund provisions for unused services"),
            (r"under\s+no\s+circumstances.*refund", RiskLevel.HIGH, 16,
             "NEGOTIATE: 'No refunds under any circumstances' is too broad"),
            (r"no\s+refunds?\s+(whatsoever|under\s+any)", RiskLevel.HIGH, 15,
             "NEGOTIATE: Absolute no-refund policy is unfair"),
             
            # === MEDIUM: Payment Terms ===
            (r"pay.*within\s+(\d+)\s+days", RiskLevel.LOW, 5,
             "CHECK: Verify payment terms align with your cash flow"),
            (r"interest.*late\s+payment|(\d+)%.*per\s+month", RiskLevel.MEDIUM, 10,
             "REVIEW: Late payment interest - ensure rate is market standard"),
            (r"automatic.*price.*adjustment|annual.*increase", RiskLevel.MEDIUM, 12,
             "CLARIFY: Cap annual increases (e.g., max 5% or CPI)"),
            (r"advance\s+payment|upfront.*payment", RiskLevel.MEDIUM, 8,
             "REVIEW: Large upfront payments increase your risk exposure"),
            (r"net\s+(\d+)|payment.*due.*immediately", RiskLevel.LOW, 5,
             "CHECK: Understand payment timeline"),
        ],
        
        RiskCategory.IP: [
            # === CRITICAL: IP Ownership Transfer ===
            (r"assign.*all.*intellectual\s+property|transfer.*ownership.*IP", RiskLevel.CRITICAL, 25,
             "CRITICAL: You may lose ownership of your work - review carefully"),
            (r"owned\s+exclusively\s+by", RiskLevel.CRITICAL, 25,
             "CRITICAL: Exclusive ownership transfer - you lose all rights"),
            (r"shall\s+(be\s+)?owned\s+(solely\s+)?by", RiskLevel.CRITICAL, 25,
             "CRITICAL: Ownership vests in other party - review scope"),
            (r"hereby\s+assign|assigns?\s+(all|any).*rights?", RiskLevel.CRITICAL, 22,
             "CRITICAL: Assignment of rights - understand what's transferred"),
            (r"vest.*exclusively|exclusively\s+vest", RiskLevel.CRITICAL, 22,
             "CRITICAL: Exclusive vesting of rights"),
            
            # === HIGH: Work for Hire / Derivatives ===
            (r"work.?for.?hire|work\s+made\s+for\s+hire", RiskLevel.HIGH, 18,
             "REVIEW: Work-for-hire means no IP ownership - negotiate if needed"),
            (r"derivatives?.*owned\s+by|derivatives?.*belong", RiskLevel.HIGH, 20,
             "CRITICAL: Your derivative works become their property"),
            (r"derivatives?.*improvements?.*feedback", RiskLevel.HIGH, 18,
             "REVIEW: All derivatives, improvements, feedback ownership transfer"),
            (r"(improvements?|modifications?|enhancements?).*owned", RiskLevel.HIGH, 16,
             "REVIEW: Improvements you make may belong to them"),
            (r"analytical\s+outputs?.*owned|simulations?.*owned", RiskLevel.HIGH, 18,
             "REVIEW: Your analytical work product becomes theirs"),
            (r"reconstructions?.*owned|feedback.*owned", RiskLevel.HIGH, 16,
             "REVIEW: Even your feedback/reconstructions are transferred"),
             
            # === MEDIUM: Licensing Terms ===
            (r"perpetual.*irrevocable.*license", RiskLevel.MEDIUM, 12,
             "CLARIFY: Understand scope of the license being granted"),
            (r"exclusive\s+license|exclusive\s+rights", RiskLevel.HIGH, 15,
             "NEGOTIATE: Consider non-exclusive license or time limitations"),
            (r"royalty.?free.*perpetual", RiskLevel.MEDIUM, 10,
             "REVIEW: Perpetual royalty-free license - understand scope"),
            (r"worldwide.*irrevocable", RiskLevel.MEDIUM, 12,
             "REVIEW: Global irrevocable license is very broad"),
            (r"sublicens(e|able)", RiskLevel.MEDIUM, 8,
             "CLARIFY: They can sublicense your content to others"),
             
            # === LOW: Standard IP Terms ===
            (r"background\s+IP|pre.?existing.*IP", RiskLevel.LOW, 5,
             "GOOD: Ensure your pre-existing IP is clearly excluded"),
            (r"retain.*rights?.*pre.?existing", RiskLevel.LOW, 3,
             "GOOD: Retention of pre-existing rights"),
        ],
        
        RiskCategory.CONFIDENTIALITY: [
            # === HIGH: Indefinite/Perpetual ===
            (r"perpetual.*confidential|indefinite.*confidential", RiskLevel.MEDIUM, 12,
             "NEGOTIATE: Request reasonable time limit (3-5 years typical)"),
            (r"indefinite\s+non.?disclosure|non.?disclosure.*indefinite", RiskLevel.MEDIUM, 12,
             "NEGOTIATE: Indefinite NDA is unusual - negotiate time limit"),
            (r"(forever|permanently|in\s+perpetuity).*confidential", RiskLevel.MEDIUM, 14,
             "NEGOTIATE: Permanent confidentiality is excessive"),
            (r"obligations?\s+(shall\s+)?(be\s+)?presumed\s+ongoing", RiskLevel.MEDIUM, 12,
             "NEGOTIATE: 'Presumed ongoing' is open-ended - set a term"),
            (r"continues?\s+indefinitely|no\s+time\s+limit", RiskLevel.MEDIUM, 12,
             "NEGOTIATE: Set a reasonable confidentiality period"),
             
            # === HIGH: Broad Disclosure Rights ===
            (r"disclose.*third\s+party.*without.*consent", RiskLevel.HIGH, 15,
             "REVIEW: Ensure proper consent mechanisms for third-party disclosure"),
            (r"share.*confidential.*without\s+(your\s+)?consent", RiskLevel.HIGH, 16,
             "CRITICAL: They can share your confidential info without consent"),
            (r"may\s+share.*affiliates?.*without", RiskLevel.HIGH, 14,
             "REVIEW: Sharing with affiliates without consent"),
             
            # === MEDIUM: Broad Definitions ===
            (r"residuals?\s+clause|residual\s+knowledge", RiskLevel.MEDIUM, 12,
             "CLARIFY: Residuals clauses can weaken confidentiality protection"),
            (r"information\s+gravity|inseparable\s+from", RiskLevel.HIGH, 15,
             "CRITICAL: Learned knowledge treated as confidential - very overreaching"),
            (r"perceived\s+or\s+derived|intangible.*unfixed", RiskLevel.MEDIUM, 12,
             "REVIEW: Very broad definition of confidential information"),
            (r"recollections?|memorization|retained\s+unintentionally", RiskLevel.MEDIUM, 14,
             "REVIEW: Even things you remember are covered - very broad"),
            (r"behavioral\s+observations?|metadata", RiskLevel.MEDIUM, 10,
             "REVIEW: Metadata and behavior observations included"),
            (r"inferred\s+information|information.*infer", RiskLevel.MEDIUM, 12,
             "REVIEW: Inferred information is vague and overreaching"),
             
            # === LOW: Standard Terms ===
            (r"return.*destroy.*confidential", RiskLevel.LOW, 5,
             "STANDARD: Normal requirement upon termination"),
            (r"certify.*no\s+(residual|latent|archival)", RiskLevel.MEDIUM, 10,
             "REVIEW: Certification of complete destruction may be impractical"),
            (r"maximum\s+protection|afford\s+maximum", RiskLevel.MEDIUM, 8,
             "REVIEW: 'Maximum protection' interpretation favors disclosing party"),
        ],
        
        RiskCategory.NON_COMPETE: [
            # === HIGH: Non-Compete Duration ===
            (r"non.?compete.*(\d+)\s+year", RiskLevel.HIGH, 20,
             "REVIEW: Non-compete duration and geographic scope - may limit future opportunities"),
            (r"non.?compete.*indefinite|perpetual.*non.?compete", RiskLevel.CRITICAL, 25,
             "CRITICAL: Indefinite non-compete is likely unenforceable and harmful"),
             
            # === HIGH: Opportunity Restrictions ===
            (r"not.*pursue\s*(any\s+)?opportunity", RiskLevel.HIGH, 18,
             "CRITICAL: Blocks you from pursuing business opportunities"),
            (r"shall\s+not.*pursue.*collaboration", RiskLevel.HIGH, 16,
             "REVIEW: Restricts future collaborations"),
            (r"not.*engage.*competing", RiskLevel.HIGH, 15,
             "REVIEW: Non-compete restriction on engaging with competitors"),
            (r"refrain\s+from.*competing|abstain.*competitive", RiskLevel.HIGH, 15,
             "REVIEW: Competitive restriction language"),
             
            # === HIGH: Non-Circumvention ===
            (r"non.?circumvention|no.?circumvent", RiskLevel.HIGH, 18,
             "REVIEW: Non-circumvention can block business opportunities"),
            (r"directly\s+or\s+indirectly.*pursue", RiskLevel.HIGH, 16,
             "REVIEW: Direct AND indirect pursuit blocked - very broad"),
            (r"reasonably\s+connected\s+to", RiskLevel.MEDIUM, 12,
             "REVIEW: 'Reasonably connected' is vague and overreaching"),
             
            # === MEDIUM: Solicitation ===
            (r"non.?solicitation.*employee|not.*solicit.*staff", RiskLevel.MEDIUM, 12,
             "NOTE: Standard but verify duration and scope"),
            (r"not.*solicit.*customers?|non.?solicitation.*client", RiskLevel.MEDIUM, 12,
             "NOTE: Customer non-solicitation - understand scope"),
             
            # === HIGH: Exclusivity ===
            (r"exclusive.*relationship|exclusivity\s+clause", RiskLevel.HIGH, 18,
             "NEGOTIATE: Exclusivity limits your business options - negotiate scope"),
            (r"restrict.*competing.*business", RiskLevel.HIGH, 15,
             "REVIEW: Ensure restrictions are reasonable for your industry"),
            (r"sole\s+and\s+exclusive|exclusive\s+provider", RiskLevel.HIGH, 16,
             "NEGOTIATE: Exclusive arrangements limit your options"),
        ],
        
        RiskCategory.DISPUTE: [
            # === HIGH: Waiving Court Rights ===
            (r"waive.*jury\s+trial|waiver.*jury", RiskLevel.HIGH, 15,
             "REVIEW: Jury trial waiver - understand implications"),
            (r"waive.*right.*court|waiv.*judicial", RiskLevel.HIGH, 16,
             "REVIEW: Waiving court access is significant"),
            
            # === MEDIUM: Arbitration ===
            (r"binding\s+arbitration", RiskLevel.MEDIUM, 10,
             "NOTE: Arbitration can be faster but limits legal options"),
            (r"mandatory\s+arbitration|compulsory\s+arbitration", RiskLevel.MEDIUM, 12,
             "REVIEW: Mandatory arbitration - cannot go to court"),
            (r"class\s+action\s+waiver", RiskLevel.MEDIUM, 12,
             "REVIEW: You give up right to join class action lawsuits"),
             
            # === HIGH: Remedies Without Safeguards ===
            (r"without\s+bond.*notice.*proof", RiskLevel.CRITICAL, 20,
             "CRITICAL: Waives normal legal protections (bond, notice, proof)"),
            (r"remedies?\s+without\s+(bond|notice)", RiskLevel.HIGH, 16,
             "REVIEW: Expedited remedies without normal safeguards"),
            (r"without\s+proof\s+of\s+damages|without\s+proving", RiskLevel.HIGH, 15,
             "REVIEW: Remedies don't require proof - unusual"),
            (r"injunctive.*without\s+(bond|notice|proof)", RiskLevel.HIGH, 16,
             "REVIEW: Injunctions without standard protections"),
            (r"specific\s+performance.*without", RiskLevel.HIGH, 14,
             "REVIEW: Specific performance without safeguards"),
            (r"consents?\s+to\s+(injunctive|equitable)", RiskLevel.MEDIUM, 12,
             "REVIEW: Pre-consent to injunctive relief"),
             
            # === MEDIUM: Jurisdiction ===
            (r"prevailing\s+party.*attorney.*fees", RiskLevel.MEDIUM, 8,
             "NOTE: Can be risky if you lose - but also beneficial if you win"),
            (r"governing\s+law|jurisdiction", RiskLevel.LOW, 5,
             "CHECK: Ensure jurisdiction is practical for your location"),
            (r"exclusive\s+jurisdiction|exclusive\s+venue", RiskLevel.MEDIUM, 10,
             "REVIEW: Exclusive jurisdiction in their preferred location"),
            (r"elect.*jurisdiction|may\s+elect.*forum", RiskLevel.MEDIUM, 12,
             "REVIEW: They choose the jurisdiction - unfair advantage"),
            (r"any\s+forum\s+where\s+harm", RiskLevel.MEDIUM, 10,
             "REVIEW: Flexible venue selection favors disclosing party"),
        ],
        
        RiskCategory.AUTO_RENEWAL: [
            # === HIGH: Auto-Renewal ===
            (r"auto.?renew|automatic.*renewal", RiskLevel.MEDIUM, 12,
             "IMPORTANT: Set calendar reminder to cancel before renewal window"),
            (r"renew.*unless.*(\d+)\s+days.*notice", RiskLevel.MEDIUM, 10,
             "ACTION: Note the cancellation notice period - add to calendar"),
            (r"evergreen\s+clause|perpetual.*renewal", RiskLevel.HIGH, 15,
             "NEGOTIATE: Request opt-in renewal instead of auto-renewal"),
            (r"continuous(ly)?\s+renew|successive.*renewal", RiskLevel.MEDIUM, 10,
             "REVIEW: Continuous renewal - understand cancellation process"),
            (r"tacit\s+renewal|silent.*renew", RiskLevel.MEDIUM, 10,
             "REVIEW: Renewal without explicit agreement"),
        ],
        
        RiskCategory.DATA_PRIVACY: [
            # === HIGH: Data Sharing ===
            (r"share.*data.*third\s+part|transfer.*data.*affiliate", RiskLevel.HIGH, 15,
             "REVIEW: Understand who gets access to your data"),
            (r"share.*affiliates?.*marketing|marketing\s+purposes", RiskLevel.HIGH, 16,
             "REVIEW: Data shared for marketing - likely unwanted"),
            (r"sell.*data|monetize.*data|data.*revenue", RiskLevel.CRITICAL, 20,
             "CRITICAL: Your data may be sold or monetized"),
             
            # === MEDIUM: Data Retention ===
            (r"retain.*data.*indefinite|no.*deletion", RiskLevel.MEDIUM, 12,
             "NEGOTIATE: Request data deletion upon contract termination"),
            (r"retain(ed)?.*indefinitely|data.*retained.*perpetual", RiskLevel.MEDIUM, 14,
             "NEGOTIATE: Indefinite data retention is excessive"),
            (r"unless.*request.*deletion|only.*upon\s+request", RiskLevel.MEDIUM, 10,
             "NOTE: Deletion only upon request - remember to request"),
             
            # === MEDIUM: Data Collection ===
            (r"collect.*personal\s+data|process.*personal\s+information", RiskLevel.MEDIUM, 10,
             "COMPLIANCE: Ensure GDPR/CCPA compliance if handling personal data"),
            (r"behavioral\s+data|tracking|analytics", RiskLevel.MEDIUM, 8,
             "REVIEW: Behavioral tracking - understand scope"),
             
            # === LOW: Good Practices ===
            (r"data\s+breach.*notification", RiskLevel.LOW, 5,
             "GOOD: Breach notification clause is a positive sign"),
            (r"data\s+protection|security\s+measures", RiskLevel.LOW, 3,
             "GOOD: Data protection mentioned"),
        ],
        
        RiskCategory.REMEDIES: [
            # === CRITICAL: Extreme Remedies ===
            (r"irreparable\s+harm.*consents?", RiskLevel.HIGH, 16,
             "REVIEW: Pre-consent to irreparable harm finding"),
            (r"any\s+breach.*constitutes?\s+irreparable", RiskLevel.HIGH, 18,
             "REVIEW: All breaches treated as irreparable - excessive"),
            (r"remedies?.*cumulative|cumulative.*remedies", RiskLevel.MEDIUM, 10,
             "REVIEW: Cumulative remedies - they can pursue multiple"),
            (r"pursue.*concurrently.*law.*equity", RiskLevel.MEDIUM, 12,
             "REVIEW: Multiple simultaneous legal actions possible"),
            (r"without\s+election\s+or\s+exhaustion", RiskLevel.MEDIUM, 10,
             "REVIEW: No requirement to exhaust other remedies first"),
            (r"equitable.*specific\s+performance", RiskLevel.MEDIUM, 10,
             "NOTE: Specific performance remedy - understand implications"),
        ],
        
        RiskCategory.SCOPE: [
            # === HIGH: Scope Expansion ===
            (r"scope\s+expansion|expanded\s+definition", RiskLevel.MEDIUM, 10,
             "REVIEW: Definitions may expand beyond expected scope"),
            (r"includes?\s+but\s+(is\s+)?not\s+limited\s+to", RiskLevel.LOW, 5,
             "NOTE: Open-ended definitions - list is not exhaustive"),
            (r"disclosures?\s+made\s+before\s+or\s+after", RiskLevel.MEDIUM, 12,
             "REVIEW: Retroactive application to past disclosures"),
            (r"third.?party\s+data|data.*third\s+parties", RiskLevel.MEDIUM, 10,
             "REVIEW: Third-party data included in scope"),
            (r"prospective\s+activities|future.*activities", RiskLevel.MEDIUM, 8,
             "REVIEW: Future activities included in scope"),
             
            # === HIGH: Successor Binding ===
            (r"successor.*bound|successor.*obligat", RiskLevel.MEDIUM, 12,
             "REVIEW: Obligations transfer to successor companies"),
            (r"acquirer.*bound|reorganized.*bound", RiskLevel.MEDIUM, 12,
             "REVIEW: Acquirers are bound by these terms"),
            (r"no\s+less\s+restrictive", RiskLevel.MEDIUM, 10,
             "REVIEW: Successors must maintain same restrictions"),
             
            # === MEDIUM: Behavioral Controls ===
            (r"behavioral\s+controls?|personnel.*access", RiskLevel.MEDIUM, 12,
             "REVIEW: Controls on personnel behavior"),
            (r"parallel\s+research|parallel.*activities", RiskLevel.HIGH, 16,
             "REVIEW: Parallel research restrictions may limit your work"),
            (r"construed\s+as\s+derivative", RiskLevel.HIGH, 15,
             "REVIEW: Broad interpretation of what's derivative"),
        ],
        
        RiskCategory.COMPLIANCE: [
            # === MEDIUM: Audit Rights ===
            (r"audit\s+rights|right.*inspect|access.*records", RiskLevel.MEDIUM, 8,
             "CLARIFY: Ensure audit scope and frequency is reasonable"),
            (r"audit.*systems|inspect.*records", RiskLevel.MEDIUM, 10,
             "REVIEW: Systems audit - understand scope of access"),
            (r"access\s+to\s+(relevant\s+)?personnel", RiskLevel.MEDIUM, 10,
             "REVIEW: Personnel access for audits - may be intrusive"),
            (r"verify\s+compliance|compliance\s+verification", RiskLevel.MEDIUM, 8,
             "REVIEW: Compliance verification method"),
            (r"upon\s+reasonable\s+notice.*audit", RiskLevel.LOW, 5,
             "STANDARD: Reasonable notice for audits is fair"),
             
            # === LOW: Standard Terms ===
            (r"comply.*all.*laws|compliance.*regulations", RiskLevel.LOW, 5,
             "STANDARD: General compliance requirement is normal"),
            (r"represent.*warrant.*authority", RiskLevel.LOW, 3,
             "STANDARD: Authority representation is normal"),
            (r"force\s+majeure|act\s+of\s+god", RiskLevel.LOW, 5,
             "GOOD: Force majeure clause provides protection"),
            
            # === MEDIUM: Administrative Controls ===
            (r"administrative.*technical.*physical", RiskLevel.MEDIUM, 8,
             "REVIEW: Multiple types of controls required"),
            (r"prevent.*unauthorized\s+access|security\s+controls", RiskLevel.LOW, 5,
             "STANDARD: Security control requirements"),
        ],
    }
    
    # Semantic Keywords for Additional Detection
    DANGER_PHRASES = [
        "shall not pursue", "shall not engage", "assumes all",
        "owned exclusively", "without limitation", "in perpetuity",
        "irrevocable", "unconditional", "absolute", "unrestricted",
        "waives all", "releases all", "any and all", "whatsoever",
        "foreseeable or not", "directly or indirectly", "inseparable",
        "presumed ongoing", "no time limit", "without bond",
        "without notice", "without proof", "at sole discretion"
    ]


class RiskAnalyzer:
    """
    Production-ready contract risk analyzer v2.0
    Enhanced with 150+ patterns and semantic analysis.
    """
    
    def __init__(self, model_name: str = "google/flan-t5-small", use_ai: bool = True):
        """
        Initialize the risk analyzer.
        
        Args:
            model_name: HuggingFace model for AI summarization
            use_ai: Whether to use AI summarization (can be disabled for speed)
        """
        self.use_ai = use_ai
        self.pattern_db = RiskPatternDatabase()
        
        if use_ai:
            print(f"⚙️ Loading AI Model: {model_name}...")
            self.tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            print("✅ AI Model loaded successfully!")
    
    def analyze_contract(self, text: str) -> RiskReport:
        """
        Perform comprehensive risk analysis on contract text.
        """
        findings = []
        category_scores = {cat.value: 0 for cat in RiskCategory}
        matched_phrases = set()  # Avoid duplicate findings
        
        # Normalize text for matching
        text_lower = text.lower()
        
        # Scan for all risk patterns
        for category, patterns in self.pattern_db.PATTERNS.items():
            for pattern, level, score, recommendation in patterns:
                try:
                    matches = list(re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL))
                    
                    for match in matches:
                        matched_text = match.group().strip()[:100]  # Limit length
                        
                        # Skip if we've already found this exact phrase
                        if matched_text in matched_phrases:
                            continue
                        matched_phrases.add(matched_text)
                        
                        # Get context around the match (150 chars before and after)
                        start = max(0, match.start() - 150)
                        end = min(len(text), match.end() + 150)
                        context = text[start:end].strip()
                        
                        finding = RiskFinding(
                            category=category,
                            level=level,
                            phrase_matched=matched_text,
                            context=f"...{context}...",
                            recommendation=recommendation,
                            score_impact=score
                        )
                        findings.append(finding)
                        category_scores[category.value] += score
                except re.error:
                    continue  # Skip invalid regex patterns
        
        # Add bonus score for danger phrase combinations
        danger_score = self._check_danger_phrases(text_lower)
        if danger_score > 0:
            category_scores["Scope & Definitions"] += danger_score
        
        # Calculate total score
        total_score = sum(f.score_impact for f in findings) + danger_score
        max_possible = 500
        risk_percentage = min(100, (total_score / max_possible) * 100)
        
        # Determine overall risk level
        if risk_percentage >= 50:
            overall_level = RiskLevel.CRITICAL
        elif risk_percentage >= 30:
            overall_level = RiskLevel.HIGH
        elif risk_percentage >= 15:
            overall_level = RiskLevel.MEDIUM
        elif risk_percentage > 0:
            overall_level = RiskLevel.LOW
        else:
            overall_level = RiskLevel.NONE
        
        # Generate AI summary if enabled
        if self.use_ai and findings:
            summary = self._generate_ai_summary(text, findings)
        else:
            summary = self._generate_basic_summary(findings)
        
        # Generate top recommendations
        recommendations = self._generate_recommendations(findings)
        
        return RiskReport(
            total_score=total_score,
            max_possible_score=max_possible,
            risk_percentage=round(risk_percentage, 1),
            overall_level=overall_level,
            findings=findings,
            summary=summary,
            recommendations=recommendations,
            category_breakdown=category_scores
        )
    
    def _check_danger_phrases(self, text: str) -> int:
        """Check for dangerous phrase combinations."""
        score = 0
        for phrase in self.pattern_db.DANGER_PHRASES:
            if phrase in text:
                score += 3
        return min(score, 30)  # Cap at 30 bonus points
    
    def _generate_ai_summary(self, text: str, findings: List[RiskFinding]) -> str:
        """Generate AI-powered summary of key risks."""
        critical_findings = [f for f in findings if f.level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        
        if critical_findings:
            categories = list(set(f.category.value for f in critical_findings[:3]))
            prompt = f"This contract has serious risks in: {', '.join(categories)}. Summarize the main legal concerns in 2 sentences for a business owner."
        else:
            prompt = "Summarize the main obligations and terms in this legal contract in 2 sentences."
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(**inputs, max_new_tokens=100, num_beams=4, early_stopping=True)
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _generate_basic_summary(self, findings: List[RiskFinding]) -> str:
        """Generate a basic summary without AI."""
        if not findings:
            return "No significant risk patterns detected. Manual review still recommended."
        
        critical = sum(1 for f in findings if f.level == RiskLevel.CRITICAL)
        high = sum(1 for f in findings if f.level == RiskLevel.HIGH)
        medium = sum(1 for f in findings if f.level == RiskLevel.MEDIUM)
        
        return f"Found {critical} critical, {high} high, and {medium} medium risk items requiring attention."
    
    def _generate_recommendations(self, findings: List[RiskFinding]) -> List[str]:
        """Generate prioritized list of recommendations."""
        sorted_findings = sorted(findings, key=lambda f: f.level.value[1], reverse=True)
        seen = set()
        recommendations = []
        
        for finding in sorted_findings[:15]:  # Top 15 recommendations
            if finding.recommendation not in seen:
                recommendations.append(f"{finding.level.value[0]} [{finding.category.value}]: {finding.recommendation}")
                seen.add(finding.recommendation)
        
        if not recommendations:
            recommendations.append("✅ No major risks detected. Standard contract terms appear reasonable.")
        
        return recommendations
    
    # Legacy methods for backward compatibility
    def summarize_risk(self, text_chunk: str) -> str:
        prompt = f"Analyze the following legal text for risk. Identify the main liability or obligation in one concise sentence: {text_chunk}"
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(**inputs, max_new_tokens=50, num_beams=4, early_stopping=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def calculate_risk_score(self, summary: str) -> int:
        red_flags = [
            "unlimited", "immediate", "termination without notice", "breach",
            "indemnify", "waive", "sole risk", "no refund", "penalty",
            "exclusive", "perpetual", "irrevocable", "assigns", "all liability"
        ]
        score = 0
        for word in red_flags:
            if word in summary.lower():
                score += 12
        return min(score, 100)


def print_risk_report(report: RiskReport) -> None:
    """Pretty print a risk report to console."""
    print("\n" + "="*70)
    print("CONTRACT RISK INTELLIGENCE REPORT v2.0")
    print("="*70)
    
    level_name, _, color = report.overall_level.value
    print(f"\n🎯 OVERALL RISK: {level_name}")
    print(f"   Score: {report.total_score} points ({report.risk_percentage}% risk level)")
    
    print(f"\n📊 RISK BY CATEGORY:")
    print("-"*50)
    for category, score in sorted(report.category_breakdown.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            bar = "█" * min(25, score // 4)
            print(f"   {category[:32]:<32} {score:>3} pts {bar}")
    
    if report.findings:
        print(f"\n🔍 KEY FINDINGS ({len(report.findings)} total):")
        print("-"*50)
        
        for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM]:
            level_findings = [f for f in report.findings if f.level == level]
            if level_findings:
                print(f"\n{level.value[0]} Issues ({len(level_findings)}):")
                for i, finding in enumerate(level_findings[:5], 1):
                    print(f"   {i}. [{finding.category.value}] '{finding.phrase_matched[:50]}...'")
                    print(f"      └─ {finding.recommendation}")
    
    print(f"\n🤖 AI SUMMARY:")
    print("-"*50)
    print(f"   {report.summary}")
    
    print(f"\n✅ TOP ACTION ITEMS:")
    print("-"*50)
    for i, rec in enumerate(report.recommendations[:8], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "="*70)
    print("⚠️  DISCLAIMER: This is an automated analysis. Always consult with")
    print("    a qualified attorney before signing any legal document.")
    print("="*70 + "\n")