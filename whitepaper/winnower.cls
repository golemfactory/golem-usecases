\ProvidesClass{winnower}

\LoadClass{article}

%\RequirePackage{longtable}%

\RequirePackage{amsmath}
\RequirePackage[noblocks]{authblk}
\RequirePackage{natbib}
\RequirePackage{hyperref} 
\RequirePackage{amssymb}
\RequirePackage{graphicx}

%  ****************************************
%  *            MACROS               *
%  ****************************************


\def\acknowledgments{\vskip 5.8mm plus 1mm minus 1mm}
\let\acknowledgements=\acknowledgments                  % second spelling

%  ****************************************
%  *            PAGE LAYOUT               *
%  ****************************************

% Page size, spacing parameters, etc. 

\RequirePackage{fullpage}
\RequirePackage{fancyhdr}


\rfoot[\thepage]{\thepage}

\def\eqsecnum{
    \@newctr{equation}[section]
    \def\theequation{\hbox{\normalsize\arabic{section}-\arabic{equation}}}}