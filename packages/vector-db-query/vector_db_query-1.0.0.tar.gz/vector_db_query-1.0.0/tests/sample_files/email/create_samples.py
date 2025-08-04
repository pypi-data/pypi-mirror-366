#!/usr/bin/env python3
"""Create sample email files for testing."""

import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mailbox
from pathlib import Path
import datetime


def create_simple_email():
    """Create a simple text email."""
    msg = MIMEText("""Dear Team,

I hope this email finds you well. I wanted to update you on the project status.

Key Updates:
- Phase 1 is complete
- Phase 2 is 50% done
- We're on track for the deadline

Please let me know if you have any questions.

Best regards,
John Doe
Project Manager""")
    
    msg['From'] = 'john.doe@company.com'
    msg['To'] = 'team@company.com'
    msg['Subject'] = 'Project Status Update - Week 12'
    msg['Date'] = email.utils.formatdate()
    msg['Message-ID'] = '<status-update-001@company.com>'
    
    with open('simple_email.eml', 'w') as f:
        f.write(msg.as_string())
    print("Created: simple_email.eml")


def create_html_email():
    """Create an email with HTML content."""
    msg = MIMEMultipart('alternative')
    msg['From'] = 'marketing@company.com'
    msg['To'] = 'customers@company.com'
    msg['Subject'] = 'New Product Launch Announcement'
    msg['Date'] = email.utils.formatdate()
    
    # Plain text version
    text = """New Product Launch!

We're excited to announce our latest product: CloudSync Pro

Features:
- Real-time synchronization
- 256-bit encryption
- Multi-platform support

Visit our website to learn more!"""
    
    # HTML version
    html = """
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background-color: #4CAF50; color: white; padding: 20px; }
                .feature { margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Product Launch!</h1>
            </div>
            <p>We're excited to announce our latest product: <strong>CloudSync Pro</strong></p>
            
            <h2>Features:</h2>
            <ul>
                <li class="feature">Real-time synchronization</li>
                <li class="feature">256-bit encryption</li>
                <li class="feature">Multi-platform support</li>
            </ul>
            
            <p>Visit our <a href="https://example.com/cloudsync">website</a> to learn more!</p>
            
            <footer>
                <p style="color: #666; font-size: 12px;">
                    © 2025 Company Inc. All rights reserved.
                </p>
            </footer>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    
    with open('html_email.eml', 'w') as f:
        f.write(msg.as_string())
    print("Created: html_email.eml")


def create_email_with_attachments():
    """Create an email with various attachments."""
    msg = MIMEMultipart()
    msg['From'] = 'reports@analytics.com'
    msg['To'] = 'management@company.com'
    msg['Cc'] = 'finance@company.com'
    msg['Subject'] = 'Q4 2024 Financial Report'
    msg['Date'] = email.utils.formatdate()
    
    # Main body
    body = """Please find attached the Q4 2024 financial report and supporting documents.

Summary:
- Revenue: $12.5M (15% increase)
- Profit: $3.2M (22% increase)
- New customers: 450

The detailed analysis is in the attached PDF report."""
    
    msg.attach(MIMEText(body))
    
    # Text attachment
    text_attach = MIMEText("""Q4 2024 Summary Data
====================

Revenue by Region:
- North America: $6.2M
- Europe: $4.1M
- Asia Pacific: $2.2M

Top Products:
1. CloudSync Pro: $5.1M
2. DataVault: $3.8M
3. SecureLink: $3.6M""")
    text_attach.add_header('Content-Disposition', 'attachment', filename='q4_summary.txt')
    msg.attach(text_attach)
    
    # CSV attachment (simulated)
    csv_data = """Region,Revenue,Growth
North America,6200000,18%
Europe,4100000,12%
Asia Pacific,2200000,25%"""
    csv_attach = MIMEText(csv_data)
    csv_attach.add_header('Content-Disposition', 'attachment', filename='regional_data.csv')
    msg.attach(csv_attach)
    
    # Binary attachment (simulated PDF)
    pdf_attach = MIMEBase('application', 'pdf')
    pdf_attach.set_payload(b'%PDF-1.4\n(Simulated PDF content)')
    encoders.encode_base64(pdf_attach)
    pdf_attach.add_header('Content-Disposition', 'attachment', filename='Q4_Report.pdf')
    msg.attach(pdf_attach)
    
    with open('email_with_attachments.eml', 'wb') as f:
        f.write(msg.as_bytes())
    print("Created: email_with_attachments.eml")


def create_thread_emails():
    """Create a series of emails representing a thread."""
    # Original email
    msg1 = MIMEText("Should we schedule a meeting to discuss the new project requirements?")
    msg1['From'] = 'alice@company.com'
    msg1['To'] = 'bob@company.com'
    msg1['Subject'] = 'New Project Discussion'
    msg1['Date'] = email.utils.formatdate()
    msg1['Message-ID'] = '<original-001@company.com>'
    
    with open('thread_1_original.eml', 'w') as f:
        f.write(msg1.as_string())
    
    # First reply
    msg2 = MIMEText("""Yes, that's a great idea. How about Tuesday at 2 PM?

> Should we schedule a meeting to discuss the new project requirements?""")
    msg2['From'] = 'bob@company.com'
    msg2['To'] = 'alice@company.com'
    msg2['Subject'] = 'Re: New Project Discussion'
    msg2['Date'] = email.utils.formatdate()
    msg2['Message-ID'] = '<reply-001@company.com>'
    msg2['In-Reply-To'] = '<original-001@company.com>'
    msg2['References'] = '<original-001@company.com>'
    
    with open('thread_2_reply.eml', 'w') as f:
        f.write(msg2.as_string())
    
    # Second reply
    msg3 = MIMEText("""Tuesday works for me. Let's also invite Carol from the design team.

> Yes, that's a great idea. How about Tuesday at 2 PM?
>> Should we schedule a meeting to discuss the new project requirements?""")
    msg3['From'] = 'alice@company.com'
    msg3['To'] = 'bob@company.com'
    msg3['Cc'] = 'carol@company.com'
    msg3['Subject'] = 'Re: Re: New Project Discussion'
    msg3['Date'] = email.utils.formatdate()
    msg3['Message-ID'] = '<reply-002@company.com>'
    msg3['In-Reply-To'] = '<reply-001@company.com>'
    msg3['References'] = '<original-001@company.com> <reply-001@company.com>'
    
    with open('thread_3_reply.eml', 'w') as f:
        f.write(msg3.as_string())
    
    print("Created: thread_1_original.eml, thread_2_reply.eml, thread_3_reply.eml")


def create_mbox_archive():
    """Create an mbox file with multiple emails."""
    mbox = mailbox.mbox('email_archive.mbox')
    
    # Email 1: Welcome email
    msg1 = email.message_from_string("""From: hr@company.com
To: newemployee@company.com
Subject: Welcome to the Team!
Date: Mon, 1 Jan 2025 09:00:00 +0000

Welcome to our company! We're excited to have you join our team.

Your onboarding schedule:
- Day 1: Orientation and paperwork
- Day 2: Team introductions
- Day 3: Project overview

Looking forward to working with you!

HR Team
""")
    mbox.add(msg1)
    
    # Email 2: Meeting reminder
    msg2 = MIMEMultipart()
    msg2['From'] = 'calendar@company.com'
    msg2['To'] = 'team@company.com'
    msg2['Subject'] = 'Reminder: Team Standup in 15 minutes'
    msg2['Date'] = email.utils.formatdate()
    msg2.attach(MIMEText('Daily standup meeting starting at 10:00 AM in Conference Room B.'))
    mbox.add(msg2)
    
    # Email 3: Newsletter
    msg3 = MIMEMultipart('alternative')
    msg3['From'] = 'newsletter@techcompany.com'
    msg3['To'] = 'subscribers@techcompany.com'
    msg3['Subject'] = 'Tech Newsletter - January 2025 Edition'
    
    text_content = """Tech Newsletter - January 2025

Top Stories:
1. AI Breakthrough in Natural Language Processing
2. Quantum Computing Reaches New Milestone
3. Cybersecurity Trends for 2025

Read more on our website!"""
    
    html_content = """
    <html>
        <body>
            <h1>Tech Newsletter - January 2025</h1>
            <h2>Top Stories:</h2>
            <ol>
                <li>AI Breakthrough in Natural Language Processing</li>
                <li>Quantum Computing Reaches New Milestone</li>
                <li>Cybersecurity Trends for 2025</li>
            </ol>
            <p><a href="https://example.com">Read more on our website!</a></p>
        </body>
    </html>"""
    
    msg3.attach(MIMEText(text_content, 'plain'))
    msg3.attach(MIMEText(html_content, 'html'))
    mbox.add(msg3)
    
    # Email 4: System notification
    msg4 = email.message_from_string("""From: noreply@system.com
To: admin@company.com
Subject: System Backup Completed Successfully
Date: Tue, 2 Jan 2025 03:00:00 +0000

Automated system backup completed successfully.

Details:
- Start time: 01:00:00
- End time: 02:45:32
- Data backed up: 2.5 TB
- Status: SUCCESS

Next scheduled backup: January 3, 2025 at 01:00:00
""")
    mbox.add(msg4)
    
    mbox.close()
    print("Created: email_archive.mbox (4 emails)")


def create_complex_email():
    """Create a complex email with multiple parts."""
    msg = MIMEMultipart('mixed')
    msg['From'] = 'project.lead@techcorp.com'
    msg['To'] = 'dev.team@techcorp.com, qa.team@techcorp.com'
    msg['Cc'] = 'management@techcorp.com'
    msg['Bcc'] = 'archive@techcorp.com'
    msg['Subject'] = 'Sprint 15 Review - Action Items and Next Steps'
    msg['Date'] = email.utils.formatdate()
    msg['Reply-To'] = 'project.lead@techcorp.com'
    msg['Importance'] = 'high'
    
    # Main multipart/alternative for body
    body_part = MIMEMultipart('alternative')
    
    # Plain text version
    text_body = """Sprint 15 Review Summary

Team,

Great work on Sprint 15! Here's a summary of our achievements and next steps:

Completed:
- User authentication module (100%)
- Database optimization (100%)
- API documentation (95%)

In Progress:
- Frontend redesign (60%)
- Performance testing (40%)

Action Items:
1. @DevTeam: Complete frontend redesign by EOW
2. @QATeam: Finalize performance test scenarios
3. @Everyone: Update Jira tickets by COB today

Next Sprint Planning: Monday, 10 AM

Thanks,
Project Lead"""
    
    body_part.attach(MIMEText(text_body, 'plain'))
    
    # HTML version with formatting
    html_body = """
    <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .completed { color: green; }
                .in-progress { color: orange; }
                .action-item { background-color: #f0f0f0; padding: 5px; margin: 5px 0; }
            </style>
        </head>
        <body>
            <h2>Sprint 15 Review Summary</h2>
            <p>Team,</p>
            <p>Great work on Sprint 15! Here's a summary of our achievements and next steps:</p>
            
            <h3>Completed:</h3>
            <ul class="completed">
                <li>User authentication module (100%)</li>
                <li>Database optimization (100%)</li>
                <li>API documentation (95%)</li>
            </ul>
            
            <h3>In Progress:</h3>
            <ul class="in-progress">
                <li>Frontend redesign (60%)</li>
                <li>Performance testing (40%)</li>
            </ul>
            
            <h3>Action Items:</h3>
            <div class="action-item">1. <strong>@DevTeam</strong>: Complete frontend redesign by EOW</div>
            <div class="action-item">2. <strong>@QATeam</strong>: Finalize performance test scenarios</div>
            <div class="action-item">3. <strong>@Everyone</strong>: Update Jira tickets by COB today</div>
            
            <p><strong>Next Sprint Planning:</strong> Monday, 10 AM</p>
            
            <p>Thanks,<br>Project Lead</p>
        </body>
    </html>"""
    
    body_part.attach(MIMEText(html_body, 'html'))
    msg.attach(body_part)
    
    # Add a JSON attachment with sprint metrics
    json_data = """{
    "sprint": 15,
    "velocity": 42,
    "completed_stories": 8,
    "bugs_fixed": 12,
    "team_satisfaction": 4.2
}"""
    json_attach = MIMEText(json_data)
    json_attach.add_header('Content-Disposition', 'attachment', filename='sprint_15_metrics.json')
    msg.attach(json_attach)
    
    with open('complex_email.eml', 'wb') as f:
        f.write(msg.as_bytes())
    print("Created: complex_email.eml")


def main():
    """Create all sample emails."""
    print("Creating sample email files...")
    
    # Change to the email directory
    email_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(email_dir)
        
        create_simple_email()
        create_html_email()
        create_email_with_attachments()
        create_thread_emails()
        create_mbox_archive()
        create_complex_email()
        
        print("\nAll sample email files created successfully!")
        print(f"Files created in: {email_dir}")
        
    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()