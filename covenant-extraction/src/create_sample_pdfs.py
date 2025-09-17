"""
Create sample PDF agreements for testing covenant extraction.
Generates realistic-looking legal documents with various covenant sections.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from datetime import datetime
from rich.console import Console

console = Console()


def create_sample_agreement_1():
    """Create a sample loan agreement with various covenants."""
    
    content = [
        ("LOAN AGREEMENT", "Title"),
        ("", "Normal"),
        ("This LOAN AGREEMENT (this 'Agreement') is entered into as of [DATE], by and between [LENDER NAME] ('Lender') and [BORROWER NAME] ('Borrower').", "Normal"),
        ("", "Normal"),
        ("ARTICLE IV", "Heading1"),
        ("COVENANTS", "Heading1"),
        ("", "Normal"),
        ("Section 4.1 Restricted Payments", "Heading2"),
        ("", "Normal"),
        ("The Borrower shall not, and shall not permit any of its Subsidiaries to, directly or indirectly:", "Normal"),
        ("", "Normal"),
        ("(a) declare or pay any dividend or make any other payment or distribution on account of the Borrower's or any of its Subsidiaries' Equity Interests (including, without limitation, any payment in connection with any merger or consolidation involving the Borrower or any of its Subsidiaries) or to the direct or indirect holders of the Borrower's or any of its Subsidiaries' Equity Interests in their capacity as such (other than dividends or distributions payable in Equity Interests (other than Disqualified Stock) of the Borrower and other than dividends or distributions payable to the Borrower or a Subsidiary of the Borrower);", "Normal"),
        ("", "Normal"),
        ("(b) purchase, redeem or otherwise acquire or retire for value (including, without limitation, in connection with any merger or consolidation involving the Borrower) any Equity Interests of the Borrower or any direct or indirect parent of the Borrower;", "Normal"),
        ("", "Normal"),
        ("(c) make any principal payment on or with respect to, or purchase, redeem, defease or otherwise acquire or retire for value any Indebtedness of the Borrower or any Guarantor that is contractually subordinated to the Obligations or to any Guarantee (excluding any intercompany Indebtedness between or among the Borrower and any of its Subsidiaries), except a payment of principal at the Stated Maturity thereof; or", "Normal"),
        ("", "Normal"),
        ("(d) make any Restricted Investment.", "Normal"),
        ("", "Normal"),
        ("Section 4.2 Limitation on Incurrence of Indebtedness", "Heading2"),
        ("", "Normal"),
        ("The Borrower will not, and will not permit any of its Subsidiaries to, directly or indirectly, create, incur, issue, assume, guarantee or otherwise become directly or indirectly liable, contingently or otherwise, with respect to (collectively, 'incur') any Indebtedness (including Acquired Debt), and the Borrower will not issue any Disqualified Stock and will not permit any of its Subsidiaries to issue any shares of preferred stock; provided, however, that the Borrower may incur Indebtedness (including Acquired Debt) or issue Disqualified Stock, if the Fixed Charge Coverage Ratio for the Borrower's most recently ended four full fiscal quarters for which internal financial statements are available immediately preceding the date on which such additional Indebtedness is incurred or such Disqualified Stock is issued, as the case may be, would have been at least 2.0 to 1.0.", "Normal"),
        ("", "Normal"),
        ("Section 4.3 Asset Sales", "Heading2"),
        ("", "Normal"),
        ("The Borrower will not, and will not permit any of its Subsidiaries to, consummate an Asset Sale unless:", "Normal"),
        ("", "Normal"),
        ("(1) the Borrower (or the Subsidiary, as the case may be) receives consideration at the time of the Asset Sale at least equal to the Fair Market Value of the assets or Equity Interests issued or sold or otherwise disposed of;", "Normal"),
        ("", "Normal"),
        ("(2) at least 75% of the consideration received in the Asset Sale by the Borrower or such Subsidiary is in the form of cash or Cash Equivalents;", "Normal"),
        ("", "Normal"),
        ("(3) the aggregate Fair Market Value of all assets sold in Asset Sales does not exceed $50,000,000 in any fiscal year.", "Normal"),
        ("", "Normal"),
        ("Section 4.4 Transactions with Affiliates", "Heading2"),
        ("", "Normal"),
        ("The Borrower will not, and will not permit any of its Subsidiaries to, make any payment to, or sell, lease, transfer or otherwise dispose of any of its properties or assets to, or purchase any property or assets from, or enter into or make or amend any transaction, contract, agreement, understanding, loan, advance or guarantee with, or for the benefit of, any Affiliate of the Borrower (each, an 'Affiliate Transaction'), unless:", "Normal"),
        ("", "Normal"),
        ("(1) the Affiliate Transaction is on terms that are no less favorable to the Borrower or the relevant Subsidiary than those that would have been obtained in a comparable transaction by the Borrower or such Subsidiary with a Person who is not an Affiliate of the Borrower; and", "Normal"),
        ("", "Normal"),
        ("(2) the Borrower delivers to the Lender with respect to any Affiliate Transaction or series of related Affiliate Transactions involving aggregate consideration in excess of $10,000,000, a resolution of the Board of Directors of the Borrower set forth in an officers' certificate certifying that such Affiliate Transaction complies with this covenant.", "Normal"),
        ("", "Normal"),
        ("ARTICLE V", "Heading1"),
        ("EVENTS OF DEFAULT", "Heading1"),
        ("", "Normal"),
        ("Section 5.1 Change of Control", "Heading2"),
        ("", "Normal"),
        ("Upon the occurrence of a Change of Control, the Borrower will make an offer (a 'Change of Control Offer') to the Lender to prepay all Obligations at a price in cash equal to 101% of the aggregate principal amount thereof, plus accrued and unpaid interest, if any, to the date of prepayment.", "Normal"),
        ("", "Normal"),
        ("'Change of Control' means the occurrence of any of the following:", "Normal"),
        ("", "Normal"),
        ("(a) the direct or indirect sale, lease, transfer, conveyance or other disposition (other than by way of merger or consolidation), in one or a series of related transactions, of all or substantially all of the properties or assets of the Borrower and its Subsidiaries taken as a whole to any 'person' (as that term is used in Section 13(d) of the Exchange Act);", "Normal"),
        ("", "Normal"),
        ("(b) the adoption of a plan relating to the liquidation or dissolution of the Borrower;", "Normal"),
        ("", "Normal"),
        ("(c) the consummation of any transaction (including, without limitation, any merger or consolidation), the result of which is that any 'person' becomes the Beneficial Owner, directly or indirectly, of more than 50% of the Voting Stock of the Borrower.", "Normal"),
        ("", "Normal"),
        ("Section 5.2 Limitation on Liens", "Heading2"),
        ("", "Normal"),
        ("The Borrower will not, and will not permit any of its Subsidiaries to, directly or indirectly, create, incur, assume or suffer to exist any Lien of any kind securing Indebtedness on any asset now owned or hereafter acquired, except Permitted Liens.", "Normal"),
        ("", "Normal"),
        ("'Permitted Liens' means:", "Normal"),
        ("", "Normal"),
        ("(1) Liens securing the Obligations;", "Normal"),
        ("(2) Liens in favor of the Borrower or any Subsidiary;", "Normal"),
        ("(3) Liens on property of a Person existing at the time such Person is merged with or into or consolidated with the Borrower or any Subsidiary;", "Normal"),
        ("(4) Liens on property existing at the time of acquisition of the property by the Borrower or any Subsidiary;", "Normal"),
        ("(5) Liens to secure Indebtedness permitted to be incurred under Section 4.2.", "Normal"),
    ]
    
    return content


def create_sample_agreement_2():
    """Create a sample bond indenture with different covenant structures."""
    
    content = [
        ("INDENTURE", "Title"),
        ("", "Normal"),
        ("Dated as of [DATE]", "Normal"),
        ("", "Normal"),
        ("Among", "Normal"),
        ("", "Normal"),
        ("[ISSUER NAME]", "Normal"),
        ("as Issuer", "Normal"),
        ("", "Normal"),
        ("and", "Normal"),
        ("", "Normal"),
        ("[TRUSTEE NAME]", "Normal"),
        ("as Trustee", "Normal"),
        ("", "Normal"),
        ("ARTICLE 10", "Heading1"),
        ("COVENANTS", "Heading1"),
        ("", "Normal"),
        ("SECTION 10.01. Limitation on Restricted Payments.", "Heading2"),
        ("", "Normal"),
        ("(a) The Company will not, and will not permit any of its Restricted Subsidiaries to, directly or indirectly, make any Restricted Payment unless, at the time of and after giving effect to such Restricted Payment:", "Normal"),
        ("", "Normal"),
        ("(1) no Default or Event of Default has occurred and is continuing or would occur as a consequence of such Restricted Payment;", "Normal"),
        ("", "Normal"),
        ("(2) the Company would, at the time of such Restricted Payment and after giving pro forma effect thereto as if such Restricted Payment had been made at the beginning of the applicable four-quarter period, have been permitted to incur at least $1.00 of additional Indebtedness pursuant to the Fixed Charge Coverage Ratio test set forth in Section 10.03(a); and", "Normal"),
        ("", "Normal"),
        ("(3) such Restricted Payment, together with the aggregate amount of all other Restricted Payments made by the Company and its Restricted Subsidiaries since the Issue Date, is less than the sum, without duplication, of:", "Normal"),
        ("", "Normal"),
        ("(A) 50% of the Consolidated Net Income of the Company for the period (taken as one accounting period) from the beginning of the first fiscal quarter commencing after the Issue Date to the end of the Company's most recently ended fiscal quarter for which internal financial statements are available at the time of such Restricted Payment;", "Normal"),
        ("", "Normal"),
        ("(B) 100% of the aggregate net cash proceeds received by the Company since the Issue Date as a contribution to its common equity capital or from the issue or sale of Equity Interests of the Company;", "Normal"),
        ("", "Normal"),
        ("(C) to the extent that any Restricted Investment that was made after the Issue Date is sold for cash or otherwise liquidated or repaid for cash, the lesser of (i) the cash return of capital with respect to such Restricted Investment and (ii) the initial amount of such Restricted Investment.", "Normal"),
        ("", "Normal"),
        ("SECTION 10.02. Limitation on Mergers and Consolidations.", "Heading2"),
        ("", "Normal"),
        ("(a) The Company will not, directly or indirectly: (1) consolidate or merge with or into another Person (whether or not the Company is the surviving corporation); or (2) sell, assign, transfer, convey or otherwise dispose of all or substantially all of the properties or assets of the Company and its Subsidiaries taken as a whole, in one or more related transactions, to another Person, unless:", "Normal"),
        ("", "Normal"),
        ("(1) either: (a) the Company is the surviving corporation; or (b) the Person formed by or surviving any such consolidation or merger (if other than the Company) or to which such sale, assignment, transfer, conveyance or other disposition has been made is a corporation organized or existing under the laws of the United States, any state of the United States or the District of Columbia;", "Normal"),
        ("", "Normal"),
        ("(2) the Person formed by or surviving any such consolidation or merger (if other than the Company) or the Person to which such sale, assignment, transfer, conveyance or other disposition has been made assumes all the obligations of the Company under the Notes and this Indenture;", "Normal"),
        ("", "Normal"),
        ("(3) immediately after such transaction, no Default or Event of Default exists;", "Normal"),
        ("", "Normal"),
        ("(4) the Company or the Person formed by or surviving any such consolidation or merger (if other than the Company), or to which such sale, assignment, transfer, conveyance or other disposition has been made would, on the date of such transaction after giving pro forma effect thereto and to any related financing transactions as if the same had occurred at the beginning of the applicable four-quarter period, be permitted to incur at least $1.00 of additional Indebtedness pursuant to the Fixed Charge Coverage Ratio test.", "Normal"),
        ("", "Normal"),
        ("SECTION 10.03. Limitation on Incurrence of Indebtedness and Issuance of Preferred Stock.", "Heading2"),
        ("", "Normal"),
        ("(a) The Company will not, and will not permit any of its Restricted Subsidiaries to, directly or indirectly, create, incur, issue, assume, guarantee or otherwise become directly or indirectly liable, contingently or otherwise, with respect to any Indebtedness and the Company will not issue any Disqualified Stock and will not permit any of its Restricted Subsidiaries to issue any shares of preferred stock; provided, however, that the Company may incur Indebtedness, if the Fixed Charge Coverage Ratio for the Company's most recently ended four full fiscal quarters for which internal financial statements are available immediately preceding the date on which such additional Indebtedness is incurred would have been at least 2.0 to 1.0, determined on a pro forma basis.", "Normal"),
        ("", "Normal"),
        ("SECTION 10.04. Limitation on Investments.", "Heading2"),
        ("", "Normal"),
        ("The Company will not, and will not permit any of its Restricted Subsidiaries to, directly or indirectly, make any Investment unless such Investment is a Permitted Investment.", "Normal"),
        ("", "Normal"),
        ("'Permitted Investments' means:", "Normal"),
        ("", "Normal"),
        ("(1) any Investment in the Company or in a Restricted Subsidiary of the Company;", "Normal"),
        ("(2) any Investment in Cash Equivalents;", "Normal"),
        ("(3) any Investment by the Company or any Restricted Subsidiary of the Company in a Person, if as a result of such Investment such Person becomes a Restricted Subsidiary of the Company;", "Normal"),
        ("(4) any Investment made as a result of the receipt of non-cash consideration from an Asset Sale that was made pursuant to and in compliance with Section 10.05;", "Normal"),
        ("(5) any acquisition of assets or Capital Stock solely in exchange for the issuance of Equity Interests (other than Disqualified Stock) of the Company;", "Normal"),
        ("(6) Investments in any Person having an aggregate Fair Market Value, taken together with all other Investments made pursuant to this clause (6) that are at that time outstanding, not to exceed $100,000,000.", "Normal"),
        ("", "Normal"),
        ("SECTION 10.05. Limitation on Asset Sales.", "Heading2"),
        ("", "Normal"),
        ("The Company will not, and will not permit any of its Restricted Subsidiaries to, consummate an Asset Sale unless:", "Normal"),
        ("", "Normal"),
        ("(1) the Company (or the Restricted Subsidiary, as the case may be) receives consideration at the time of the Asset Sale at least equal to the Fair Market Value of the assets or Equity Interests issued or sold or otherwise disposed of; and", "Normal"),
        ("", "Normal"),
        ("(2) at least 75% of the consideration received in the Asset Sale by the Company or such Restricted Subsidiary is in the form of cash or Cash Equivalents.", "Normal"),
    ]
    
    return content


def create_pdf(content, filename, title_text="LEGAL AGREEMENT"):
    """Create a PDF from content list."""
    doc = SimpleDocTemplate(str(filename), pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='DocTitle', parent=styles['Title'], 
                            fontSize=18, alignment=TA_CENTER, spaceAfter=30))
    styles.add(ParagraphStyle(name='CustomHeading1', parent=styles['Heading1'], 
                            fontSize=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'], 
                            fontSize=12, spaceAfter=10))
    
    # Add content
    for text, style in content:
        if text:
            if style == "Title":
                elements.append(Paragraph(text, styles['DocTitle']))
            elif style == "Heading1":
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(text, styles['CustomHeading1']))
            elif style == "Heading2":
                elements.append(Spacer(1, 6))
                elements.append(Paragraph(text, styles['CustomHeading2']))
            else:
                elements.append(Paragraph(text, styles['Justify']))
        else:
            elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)


def create_sample_pdfs():
    """Create all sample PDFs."""
    data_dir = Path("/workspace/covenant-extraction/data")
    data_dir.mkdir(exist_ok=True)
    
    # Create sample agreement 1
    console.print("[cyan]Creating sample_loan_agreement.pdf...[/cyan]")
    content1 = create_sample_agreement_1()
    create_pdf(content1, data_dir / "sample_loan_agreement.pdf", "LOAN AGREEMENT")
    console.print("[green]✓ Created sample_loan_agreement.pdf[/green]")
    
    # Create sample agreement 2
    console.print("[cyan]Creating sample_bond_indenture.pdf...[/cyan]")
    content2 = create_sample_agreement_2()
    create_pdf(content2, data_dir / "sample_bond_indenture.pdf", "INDENTURE")
    console.print("[green]✓ Created sample_bond_indenture.pdf[/green]")
    
    # Create a combined/complex agreement
    console.print("[cyan]Creating sample_complex_agreement.pdf...[/cyan]")
    combined_content = [
        ("CREDIT AGREEMENT", "Title"),
        ("", "Normal"),
        ("This CREDIT AGREEMENT dated as of " + datetime.now().strftime("%B %d, %Y"), "Normal"),
        ("", "Normal"),
    ]
    
    # Add sections from both agreements with some modifications
    combined_content.extend(content1[4:20])  # Restricted payments
    combined_content.append(("", "Normal"))
    combined_content.extend(content2[18:35])  # Various covenants from indenture
    combined_content.append(("", "Normal"))
    combined_content.extend(content1[35:])   # Change of control and liens
    
    create_pdf(combined_content, data_dir / "sample_complex_agreement.pdf", "CREDIT AGREEMENT")
    console.print("[green]✓ Created sample_complex_agreement.pdf[/green]")
    
    console.print(f"\n[bold green]✓ All sample PDFs created in {data_dir}[/bold green]")


if __name__ == "__main__":
    create_sample_pdfs()