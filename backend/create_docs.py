from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def create_pdf(filename, title, lines):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=14, fontName='Helvetica-Bold', spaceAfter=10)
    body_style = ParagraphStyle('body', fontSize=10, fontName='Helvetica', spaceAfter=4)

    story = [Paragraph(title, title_style), Spacer(1, 6)]
    for line in lines:
        if line.strip() == "":
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(line.strip(), body_style))

    doc.build(story)
    print(f"Created: {filename}")

backend_lines = [
    "Environment Setup",
    "1. Install Node.js version 18 or above from nodejs.org",
    "2. Install Git from git-scm.com",
    "3. Clone the backend repository using git clone",
    "4. Run npm install to install all dependencies",
    "5. Copy .env.example to .env and fill in the values",
    "6. Run npm run dev to start the local server on port 3000",
    "",
    "API Standards",
    "All endpoints must follow REST conventions",
    "Use camelCase for JSON keys",
    "Always return proper HTTP status codes",
    "Add JSDoc comments for every function",
    "",
    "Database Setup",
    "We use PostgreSQL as primary database",
    "Run migrations using npm run migrate",
    "Never modify migration files directly",
]

frontend_lines = [
    "Environment Setup",
    "1. Install Node.js version 18 or above",
    "2. Clone frontend repo using git clone",
    "3. Run npm install",
    "4. Run npm run dev to open app at localhost 5173",
    "",
    "Component Guidelines",
    "Use functional components only",
    "All components must have PropTypes defined",
    "Use TailwindCSS for styling",
    "Follow BEM naming for custom CSS",
    "",
    "Design System",
    "Access Figma at figma.com company design system",
    "Primary color is 6366F1",
    "Font is Inter",
    "Always use design tokens not hardcoded values",
]

hr_lines = [
    "Working Hours",
    "Office hours are 9 AM to 6 PM IST",
    "Flexible work from home 2 days per week",
    "Core hours when everyone must be online 11 AM to 4 PM",
    "",
    "Leave Policy",
    "12 casual leaves per year",
    "12 sick leaves per year",
    "15 earned leaves per year",
    "Apply leaves minimum 2 days in advance on HR portal",
    "",
    "Code of Conduct",
    "Respect all colleagues",
    "No discrimination of any kind",
    "Report issues to hr at company dot com",
    "",
    "Tools Access",
    "GitHub access request via IT portal",
    "Slack invite sent on joining email",
    "Jira manager will add you to the project",
]

create_pdf("documents/backend_guide.pdf", "Backend Developer Onboarding Guide", backend_lines)
create_pdf("documents/frontend_guide.pdf", "Frontend Developer Onboarding Guide", frontend_lines)
create_pdf("documents/hr_policies.pdf", "HR Policies and Company Guidelines", hr_lines)