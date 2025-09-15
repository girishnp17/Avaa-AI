"""
Professional LaTeX Resume Templates
Optimized for ATS compatibility and visual appeal
"""

# Improved Professional Tech Template - Fixed without fontawesome dependency
MINIMAL_TECH_TEMPLATE = r"""
\documentclass[10pt,letterpaper]{{article}}

% Essential packages
\usepackage[margin=0.7in]{{geometry}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{titlesec}}
\usepackage{{enumitem}}
\usepackage{{hyperref}}
\usepackage{{xcolor}}
\usepackage{{tabularx}}

% Color scheme - Professional tech colors
\definecolor{{techblue}}{{RGB}}{{0, 102, 204}}
\definecolor{{darkgray}}{{RGB}}{{64, 64, 64}}
\definecolor{{lightgray}}{{RGB}}{{128, 128, 128}}

% Remove page numbers
\pagestyle{{empty}}

% Configure hyperlinks
\hypersetup{{
    colorlinks=true,
    linkcolor=techblue,
    urlcolor=techblue,
    pdftitle={{{full_name} - Software Engineer Resume}},
    pdfauthor={{{full_name}}}
}}

% Section formatting with better spacing
\titleformat{{\section}}{{
    \color{{techblue}}\large\bfseries
}}{{}}{{0em}}{{}}[{{\color{{techblue}}\titlerule[1pt]}}]

\titlespacing{{\section}}{{0pt}}{{12pt}}{{8pt}}

% No paragraph indentation
\setlength{{\parindent}}{{0pt}}

% Enhanced custom commands
\newcommand{{\sectiontitle}}[1]{{
    \section{{#1}}
}}

\newcommand{{\jobtitle}}[4]{{
    \noindent
    \begin{{tabularx}}{{\textwidth}}{{X r}}
        \textbf{{\color{{darkgray}}#1}} & \textbf{{\color{{darkgray}}#2}} \\
        \textit{{\color{{lightgray}}\small #3}} & \textit{{\color{{lightgray}}\small #4}} \\
    \end{{tabularx}}
    \vspace{{2pt}}
}}

\newcommand{{\achievement}}[1]{{
    \noindent$\bullet$ \small #1 \\[2pt]
}}

\newcommand{{\projectheader}}[3]{{
    \noindent
    \begin{{tabularx}}{{\textwidth}}{{X r}}
        \textbf{{\color{{darkgray}}#1}} & \textbf{{\color{{lightgray}}\small #2}} \\
        \textit{{\color{{lightgray}}\small #3}} & \\
    \end{{tabularx}}
    \vspace{{2pt}}
}}

\newcommand{{\education}}[3]{{
    \noindent
    \begin{{tabularx}}{{\textwidth}}{{X r}}
        \textbf{{\color{{darkgray}}#1}} & \textbf{{\color{{lightgray}}\small #3}} \\
        \textit{{\color{{lightgray}}\small #2}} & \\
    \end{{tabularx}}
    \vspace{{2pt}}
}}

\begin{{document}}

%-----PROFESSIONAL HEADER-----
\begin{{center}}
    {{\LARGE\textbf{{\color{{darkgray}}{full_name}}}}}\\
    \vspace{{8pt}}
    \color{{lightgray}}\small
    Email: {email} \quad $|$ \quad
    Phone: {phone} \quad $|$ \quad
    Location: {location} \\
    \vspace{{4pt}}
    \href{{{linkedin_url}}}{{LinkedIn Profile}} \quad $|$ \quad
    \href{{{portfolio_url}}}{{Portfolio}}
\end{{center}}

\vspace{{10pt}}

%-----PROFESSIONAL SUMMARY-----
\sectiontitle{{Professional Summary}}
\noindent {summary}

\vspace{{8pt}}

%-----TECHNICAL SKILLS-----
\sectiontitle{{Technical Skills}}
\noindent {skills}

\vspace{{8pt}}

%-----PROFESSIONAL EXPERIENCE-----
{experience_section}

%-----EDUCATION-----
{education_section}

%-----KEY PROJECTS-----
{projects_section}

%-----CERTIFICATIONS-----
{certifications_section}

\end{{document}}
"""

# Use only the tech template
DEFAULT_TEMPLATE = MINIMAL_TECH_TEMPLATE