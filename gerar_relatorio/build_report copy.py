def base_structure(results):
    content = r"""\documentclass{article}

    \usepackage{charter} 

    \usepackage[
        a4paper,
        top=1in,
        bottom=1in,
        left=1in,
        right=1in,
    ]{geometry}

    \setlength{\parindent}{0pt}
    \setlength{\parskip}{1em}

    \usepackage{graphicx}

    \usepackage{fancyhdr} 
    \usepackage{hyperref}

    \fancypagestyle{firstpage}{
        \fancyhf{}
        \renewcommand{\headrulewidth}{0pt}
        \renewcommand{\footrulewidth}{1pt}
    }

    \fancypagestyle{subsequentpages}{
        \fancyhf{}
        \renewcommand{\headrulewidth}{1pt}
        \renewcommand{\footrulewidth}{1pt}
    }

    \AtBeginDocument{\thispagestyle{firstpage}}
    \pagestyle{subsequentpages}

    \begin{document}

    \includegraphics[width=0.3\textwidth]{LogoRiverEye.jpg}

    \vspace{-3em}

    \rule{\linewidth}{1pt}
    \rule{\linewidth}{1pt}

    \hfill
    \begin{tabular}{l @{}}
        \today \bigskip\\
        Automatic Generated Report \\
        API version: {1.2} \\
        River Eye \\
        123 Rivereye Address \\
        City, State 12345 \\
        Contact Info: \href{mailto:rivereyeapp@gmail.com}{rivereyeapp@gmail.com}
    \end{tabular}


    \section{River Eye PPA Analisys Report}
    This is an automatically generated report by the RiverEye API, \url{http://www.rivereye.com} the following are APP reports on each of the user select regions.
    \bigskip

    %(result)s

    \section{Recommended Deflorestation Services:}
    \begin{itemize}
        \item Service 1 - Website: \url{} - Address - phone - email
        \item Service 2 - Website: \url{} - Address - phone - email
        \item Service 3 - Website: \url{} - Address - phone - email
    \end{itemize}

    \vspace{25pt}


    \end{document}

    """
    return content%results

def generate_result(area_results):
    area_results['total_area'] = area_results['irregular_area'] + area_results['river_area'] + area_results['veg_area'] + area_results['nveg_area']
    area_results['estimated_cost'] = area_results['irregular_area'] * area_results['cost']
    content = r"""\subsection{Area %(i)s}

    \begin{minipage}{0.5\linewidth}

    GPS Coordinates: %(gps_S)s$^{\circ}$ S, %(gps_W)s$^{\circ}$ W    \\
    PPA Irregular Area: %(irregular_area)s $ha$  \\
    River Area: %(river_area)s $ha$              \\
    Vegetation Area: %(veg_area)s $ha$           \\
    Non Vegetation: %(nveg_area)s $ha$           \\
    Total Area: %(total_area)s $ha$              \\
    Cost \$~/~$ha$: %(cost)s               \\
    \rule{\linewidth}{1pt}
    \textbf{Estimated Cost:} \$ %(estimated_cost)s           \\
    \rule{\linewidth}{1pt}

    \end{minipage}\hfil
    \begin{minipage}{0.5\linewidth}
        \includegraphics[width=\linewidth]{%(fname)s}
    \end{minipage}
    
    """

    return content%area_results
    