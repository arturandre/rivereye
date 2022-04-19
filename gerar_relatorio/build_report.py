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

    \begin{minipage}{0.6\linewidth}
        \includegraphics[width=0.7\linewidth]{LogoRiverEye.jpg}
    \end{minipage}\hfil
    \begin{minipage}{0.4\linewidth}
        \today \bigskip \\
        Automatic Generated Report \\
        API version: {1.2} \\
        River Eye \\
        123 Rivereye Address \\
        City, State 12345 \\
        Contact Info: \href{mailto:rivereyeapp@gmail.com}{rivereyeapp@gmail.com} \\

    
    \end{minipage}
    \vspace{-3em}

    \rule{\linewidth}{1pt}
    \rule{\linewidth}{1pt}

    \hfill


    \section{River Eye PPA Analisys Report}
    This is an automatically generated report by the RiverEye API, \url{http://www.rivereye.com} the following are APP reports on each of the user select regions.
    \bigskip

    %(result)s

    \section{Recommended Deflorestation Services:}
    \begin{itemize}
        \item Green Sao Paulo - Website: \url{https://greensaopaulo.com.br/} - Rua Evans, 627, Vila Esperanca, Sao Paulo/SP, CEP: 03648-020 - (11) 94330-4540 - \href{mailto:contato@greensaopaulo.com.br}{contato@greensaopaulo.com.br}
        \item BioFlora Comercial - Website: \url{http://www.viveirobioflora.com.br/} - Rod. Piracicaba, Piracicaba/SP, CEP: 13420-280 - (19) 3414-4763 - \href{mailto:vendas@viveirobioflora.com.br}{vendas@viveirobioflora.com.br}
        \item Forte Florestal - Website: \url{https://forteflorestal.com/} - Av. Vitorio Ongaratto, 926, Sala 04 Jacupiranga/SP, CEP: 11940-000 -  (11) 96905-0354 - \href{mailto:atendimento@forteflorestal.com.br}{atendimento@forteflorestal.com.br}
        \item Dantas Ambiental - Website: \url{https://dantasambiental.com.br/} - Rua Napoleao Selmi Dei, 676, Sala 02, Vila Harmonia, Araraquara/SP, CEP: 14802-500 -\\ (11) 99789-0543 - \href{mailto:comercial@dantasambiental.com.br}{comercial@dantasambiental.com.br}
        \item Programa Nascentes - Website: \url{http://www.programanascentes.sp.gov.br/}


        
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
    