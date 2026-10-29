% Sidenotes: a Chinese textbook class reconstructed from seven reference images.
% Copyright 2026. Original template code: MIT License (see LICENSE).
\NeedsTeXFormat{LaTeX2e}[2022/06/01]
\ProvidesClass{sidenotes}[2026/10/25 v1.1 Simplex-default Chinese textbook]
\newif\ifSNmono
\newif\ifSNfixed
\SNfixedtrue
\DeclareOption{monochrome}{\SNmonotrue}
\DeclareOption{onesidebar}{\SNfixedtrue}
\DeclareOption{simplex}{\SNfixedtrue}
\DeclareOption{oneside}{\SNfixedtrue}
\DeclareOption{duplex}{\SNfixedfalse}
\DeclareOption{twoside}{\SNfixedfalse}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions*\relax
\ifSNfixed\PassOptionsToClass{oneside}{book}\else\PassOptionsToClass{twoside}{book}\fi
\LoadClass[10pt,a4paper,openany]{book}
\RequirePackage{iftex}
\RequirePackage{fix-cm}
\ifXeTeX\else\ClassError{sidenotes}{Use XeLaTeX}{Compile with xelatex.}\fi
\RequirePackage{fontspec}
% Local xeCJK support files make smaller TeX installations usable.
\RequirePackage{xeCJK}
\setmainfont{NimbusRoman}[Path=fonts/,Extension=.otf,UprightFont=*-Regular,
  BoldFont=*-Bold,ItalicFont=*-Italic,BoldItalicFont=*-BoldItalic]
\setsansfont{NimbusSans}[Path=fonts/,Extension=.otf,UprightFont=*-Regular,
  BoldFont=*-Bold,ItalicFont=*-Italic,BoldItalicFont=*-BoldItalic]
\setmonofont{DejaVuSansMono}[Path=fonts/,Extension=.ttf,
  UprightFont=*,BoldFont=*-Bold,Scale=0.95]
\setCJKmainfont{NotoSerifSC-Regular.otf}[Path=fonts/,
  BoldFont=NotoSerifSC-Bold.otf,ItalicFont=NotoSerifSC-Regular.otf]
\setCJKsansfont{NotoSansSC-Regular.otf}[Path=fonts/,BoldFont=NotoSansSC-Bold.otf]
\setCJKmonofont{NotoSansSC-Regular.otf}[Path=fonts/]
\newfontfamily\SNsymbolfont{NotoSerifSC-Regular.otf}[Path=fonts/]
\xeCJKsetup{PunctStyle=quanjiao,CJKmath=true}
\RequirePackage{geometry}
\geometry{a4paper,inner=24mm,outer=78mm,top=28mm,bottom=28mm,
  marginparwidth=48mm,marginparsep=6mm,headheight=0pt,headsep=0pt,footskip=12mm}
\ifSNfixed\geometry{twoside=false,left=24mm,right=78mm}\fi
\RequirePackage[table]{xcolor}
\RequirePackage{amsmath,amssymb,mathtools}
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc,fit,backgrounds,shapes.geometric,
  decorations.pathreplacing,matrix}
\RequirePackage[most]{tcolorbox}
\RequirePackage{booktabs,tabularx,array,multicol,enumitem}
\RequirePackage{marginnote,needspace,changepage,eso-pic,titlesec}
\RequirePackage{listings}
\RequirePackage{hyperref}
\hypersetup{unicode=true,colorlinks=true,linkcolor=SNink,urlcolor=SNink,
  bookmarksnumbered=true,pdfcreator={XeLaTeX / Sidenotes},
  pdftitle={边栏讲义模板},pdfauthor={}}
\AtBeginDocument{\ifSNfixed\typeout{SIDENOTES-PRINT-MODE: simplex}\else
  \typeout{SIDENOTES-PRINT-MODE: duplex}\fi}
\definecolor{SNblue}{HTML}{DDEFF5}
\definecolor{SNpink}{HTML}{F7E0EB}
\definecolor{SNyellow}{HTML}{FFF1B4}
\definecolor{SNgreen}{HTML}{DFEFE6}
\definecolor{SNgray}{HTML}{F6F6F6}
\definecolor{SNink}{HTML}{466C82}
\definecolor{SNmuted}{HTML}{858585}
\definecolor{SNrose}{HTML}{AD7B95}
\definecolor{SNnode}{HTML}{CAD7EA}
\ifSNmono
  \colorlet{SNblue}{black!7}\colorlet{SNpink}{black!11}
  \colorlet{SNyellow}{black!6}\colorlet{SNgreen}{black!9}
  \colorlet{SNink}{black}\colorlet{SNrose}{black!65}
  \colorlet{SNnode}{black!17}
\fi
\makeatletter
\renewcommand\normalsize{\@setfontsize\normalsize{10pt}{13pt}
  \abovedisplayskip 7pt plus2pt minus2pt\belowdisplayskip 7pt plus2pt minus2pt
  \abovedisplayshortskip 3pt plus2pt\belowdisplayshortskip 5pt plus2pt}
\makeatother
\normalsize
\setlength{\parindent}{2em}
\setlength{\parskip}{2.5pt plus0.8pt}
\setlength{\emergencystretch}{1.2em}
\raggedbottom\pagestyle{empty}
\setcounter{secnumdepth}{2}\setcounter{tocdepth}{1}
\setlist{nosep,leftmargin=1.6em,labelsep=.45em,topsep=3pt}
\titleformat{\section}{\bfseries\fontsize{14}{20}\selectfont}
  {\thesection}{.6em}{}
\titlespacing*{\section}{0pt}{7mm plus1mm minus1mm}{3mm}
\titleformat{\subsection}{\bfseries\fontsize{11.3}{16}\selectfont}
  {\thesubsection}{.6em}{}
\titlespacing*{\subsection}{0pt}{4mm}{2mm}
\newcommand{\SNchaptertitle}{}
\newcommand{\SNsectiontitle}{}
\newcommand{\SNopeningpage}{-1000}
\renewcommand{\chaptermark}[1]{\gdef\SNchaptertitle{#1}}
\renewcommand{\sectionmark}[1]{\gdef\SNsectiontitle{\thesection\enspace#1}}
\RenewDocumentCommand\chapter{s o m}{%
  \clearpage
  \IfBooleanTF{#1}{\chaptermark{#3}}{%
    \refstepcounter{chapter}\chaptermark{#3}%
    \addcontentsline{toc}{chapter}{\protect\numberline{\thechapter}#3}}%
  \xdef\SNopeningpage{\thepage}\gdef\SNsectiontitle{}%
  \vspace*{6mm}}
% Simplex keeps headers and sidebars on the same side; duplex mirrors both.
\newcommand{\SNheaderRight}{%
  \draw[line width=.45pt] ([xshift=-34.5mm]current page.north east)--++(0,-16mm);
  \node[anchor=south east,inner sep=0pt,font=\small]
    at ([xshift=-38mm,yshift=-15.5mm]current page.north east){\SNsectiontitle};
  \node[anchor=south west,inner sep=0pt,font=\small]
    at ([xshift=-31.5mm,yshift=-15.5mm]current page.north east){\thepage};}
\newcommand{\SNheaderLeft}{%
  \draw[line width=.45pt] ([xshift=34.5mm]current page.north west)--++(0,-16mm);
  \node[anchor=south east,inner sep=0pt,font=\small]
    at ([xshift=31.5mm,yshift=-15.5mm]current page.north west){\thepage};
  \node[anchor=south west,inner sep=0pt,font=\small]
    at ([xshift=37.5mm,yshift=-15.5mm]current page.north west)
    {\thechapter\enspace\SNchaptertitle};}
% The vertical header rules extend to the physical top edge, as in the references.
\AddToShipoutPictureBG{%
  \begin{tikzpicture}[remember picture,overlay]
  \ifnum\value{page}=\SNopeningpage\relax
    \ifSNfixed\def\SNheadx{134.5}\else
      \ifodd\value{page}\def\SNheadx{134.5}\else\def\SNheadx{186}\fi\fi
    \draw[line width=.5pt] ([xshift=\SNheadx mm]current page.north west)
      --++(0,-36mm);
    \node[anchor=south east,inner sep=0pt,font=\fontsize{21}{25}\selectfont]
      at ([xshift=\dimexpr\SNheadx mm-3mm\relax,yshift=-36mm]current page.north west)
      {\SNchaptertitle};
    \node[anchor=south west,inner sep=0pt,font=\bfseries\fontsize{62}{64}\selectfont]
      at ([xshift=\dimexpr\SNheadx mm+3mm\relax,yshift=-36mm]current page.north west)
      {\thechapter};
  \else
    \ifSNfixed\SNheaderRight\else
      \ifodd\value{page}\SNheaderRight\else\SNheaderLeft\fi\fi
  \fi
  \end{tikzpicture}}
\renewcommand{\marginfont}{\fontsize{8.5}{10.7}\selectfont}
\newcommand{\SideFont}{\fontsize{8.5}{10.7}\selectfont}
\NewDocumentCommand\Sidebar{O{0pt} m +m}{%
  \marginnote{\SideFont\raggedright\setlength{\parindent}{0pt}%
    \textbf{#2}\par\vspace{1.3mm}#3}[#1]}
\NewDocumentCommand\SideFigure{O{0pt} m +m}{%
  \marginnote{\SideFont\setlength{\parindent}{0pt}%
    \centering#3\par\vspace{2mm}\refstepcounter{figure}%
    \raggedright\textbf{图\thefigure:}\enspace#2}[#1]}
\NewDocumentCommand\MainFigure{s m +m}{%
  \par\vspace{2mm}\noindent\begin{minipage}{\linewidth}
  \centering#3\par\vspace{2mm}%
  {\small\raggedright\IfBooleanF{#1}{\refstepcounter{figure}图\thefigure:\enspace}#2\par}%
  \end{minipage}\par\vspace{2mm}}
\newcommand{\Lead}[1]{\par\noindent\textbf{#1}\quad}
\newcommand{\Key}[1]{\textbf{#1}}
\newcommand{\InlineCode}[1]{{\ttfamily\small\detokenize{#1}}}
\newcommand{\BigO}[1]{\ensuremath{\mathcal O(#1)}}
\newcommand{\SNqed}{\hfill\ensuremath{\square}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\tcbset{SNbase/.style={enhanced,breakable,sharp corners,boxrule=0pt,
  frame hidden,left=2mm,right=2mm,top=1.7mm,bottom=1.7mm,
  before skip=3mm,after skip=3mm,parbox=false,fontupper=\normalsize}}
% Each semantic environment has its own section-based counter.
\NewDocumentCommand\SNDeclareBox{m m m}{%
  \newcounter{#1}[section]%
  \expandafter\renewcommand\csname the#1\endcsname{\thesection.\arabic{#1}}%
  \newenvironment{#1}[1][]{\refstepcounter{#1}%
    \begin{tcolorbox}[SNbase,colback=#3]%
    \noindent\textbf{#2\csname the#1\endcsname}%
    \if\relax\detokenize{##1}\relax\else\enspace(##1)\fi\enspace\ignorespaces}
    {\end{tcolorbox}}}
\SNDeclareBox{definition}{定义}{SNblue}
\SNDeclareBox{theorem}{定理}{SNyellow}
\SNDeclareBox{example}{例}{SNpink}
\SNDeclareBox{exercise}{练习}{SNgreen}
\SNDeclareBox{proposition}{命题}{SNyellow}
\SNDeclareBox{corollary}{推论}{SNyellow}
\SNDeclareBox{examproblem}{考题}{SNblue}
\NewDocumentEnvironment{proof}{O{证明}}{\par\noindent\textbf{#1}\quad\ignorespaces}
  {\SNqed\par\vspace{2mm}}
\NewDocumentEnvironment{solution}{O{解析}}{\par\noindent\textbf{#1}\quad\ignorespaces}
  {\par\vspace{2mm}}
\newtcolorbox{pitfall}[1][易错点]{SNbase,colback=SNpink,
  before upper={\noindent\textbf{#1}\quad}}
\newtcolorbox{takeaway}[1][结论速记]{SNbase,colback=SNyellow,
  before upper={\noindent\textbf{#1}\quad}}
\newtcolorbox{summarybox}[1][本节小结]{SNbase,colback=SNgreen,
  before upper={\noindent\textbf{#1}\quad}}
\newtcolorbox{methodbox}[1][方法]{SNbase,colback=SNgray,
  borderline west={1.2pt}{0pt}{SNink},before upper={\noindent\textbf{#1}\quad}}
\newtcolorbox{algorithm}[1][算法]{SNbase,colback=SNgray,
  before upper={\noindent\textbf{#1}\par\vspace{2mm}}}
\newenvironment{steps}{\begin{enumerate}[label=\textcolor{SNink}{\arabic*.},
  itemsep=3pt,leftmargin=1.7em]}{\end{enumerate}}
\newcommand{\Choices}[4]{\par\smallskip\noindent
  \begin{tabularx}{\linewidth}{@{}YY@{}}A. #1&B. #2\\[2pt]C. #3&D. #4\end{tabularx}}
\NewDocumentCommand\AnswerLink{m}{\hyperlink{answer:#1}{\textcolor{SNink}{答案与解析\,$\rightarrow$}}}
\NewDocumentCommand\QuestionAnchor{m}{\hypertarget{question:#1}{}}
\NewDocumentCommand\AnswerAnchor{m}{\hypertarget{answer:#1}{}}
\NewDocumentCommand\BackToQuestion{m}{\hyperlink{question:#1}{\textcolor{SNink}{$\leftarrow$\,返回题目}}}
\newcommand{\FillIn}[1][22mm]{\rule[-1.3pt]{#1}{.35pt}}
\newcommand{\CheckItem}[1]{\par\noindent\makebox[1.4em][l]{$\square$}#1}
\NewDocumentCommand\NoteLines{O{4}}{\par\medskip
  \foreach \i in {1,...,#1}{\noindent\textcolor{black!17}{\rule{\linewidth}{.3pt}}\par\vspace{4mm}}}
\NewDocumentCommand\DotGrid{O{30mm}}{\par\smallskip\noindent
  \begin{tikzpicture}\clip (0,0) rectangle (\linewidth,#1);
    \foreach \x in {0,4,...,108}\foreach \y in {0,4,...,100}
    \fill[black!23] (\x mm,\y mm) circle (.18mm);
    \path (0,0) rectangle (\linewidth,#1);\end{tikzpicture}\par}
\newenvironment{wideblock}{\ifSNfixed\begin{adjustwidth}{0mm}{-54mm}\else
  \begin{adjustwidth*}{0mm}{-54mm}\fi}{\ifSNfixed\end{adjustwidth}\else\end{adjustwidth*}\fi}
\newtcolorbox{recallcard}[1][主动回忆]{SNbase,colback=white,
  borderline={.4pt}{0pt}{black!25},before upper={\noindent\textbf{#1}\par\smallskip}}
\newcommand{\Term}[2]{\par\noindent\textbf{#1}\enspace#2}
\lstdefinestyle{SNcode}{language=C++,basicstyle=\ttfamily\fontsize{8.2}{10.5}\selectfont,
  keywordstyle=\color{SNink}\bfseries,commentstyle=\color{SNmuted},
  stringstyle=\color{SNrose},numbers=left,numberstyle=\fontsize{6}{7.5}\selectfont\color{SNmuted},
  numbersep=5pt,frame=single,rulecolor=\color{SNgray},framerule=4pt,
  framesep=1.5mm,xleftmargin=3.2mm,xrightmargin=1mm,
  backgroundcolor=\color{white},showstringspaces=false,columns=fullflexible,
  keepspaces=true,breaklines=true,breakatwhitespace=false,tabsize=2,
  literate={…}{{\char"2026}}1,
  aboveskip=3mm,belowskip=3mm,escapeinside={(*@}{@*)}}
\newcommand{\SNlinebg}{\color{white}}
% \BlueLines{3,6} and \PinkLines{8,9} reset independently for each listing.
\newcommand{\SNbluelines}{}
\newcommand{\SNpinklines}{}
\newcommand{\BlueLines}[1]{\def\SNbluelines{#1}}
\newcommand{\PinkLines}[1]{\def\SNpinklines{#1}}
\makeatletter
\renewcommand{\SNlinebg}{\color{white}%
  \edef\SNcurrentline{\number\value{lstnumber}}%
  \@for\SNtest:=\SNbluelines\do{\ifx\SNcurrentline\SNtest\color{SNblue}\fi}%
  \@for\SNtest:=\SNpinklines\do{\ifx\SNcurrentline\SNtest\color{SNpink}\fi}}
\lst@AddToHook{EveryPar}{\rlap{\begingroup\SNlinebg
  \rule[-.65ex]{\linewidth}{2.2ex}\endgroup}}
\makeatother
\NewDocumentCommand\CodeFile{O{} m}{\lstinputlisting[style=SNcode,#1]{#2}%
  \BlueLines{}\PinkLines{}}
\lstnewenvironment{codeblock}[1][]{\lstset{style=SNcode,#1}}{\BlueLines{}\PinkLines{}}
\newcommand{\SNtablehead}{\rowcolor{SNblue}}
\newcommand{\NewPage}{\clearpage}
\endinput
