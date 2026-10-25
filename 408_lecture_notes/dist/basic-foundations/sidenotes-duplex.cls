% Explicit double-sided entry point. See LICENSE.
\NeedsTeXFormat{LaTeX2e}[2022/06/01]
\ProvidesClass{sidenotes-duplex}[2026/10/25 v1.1 Double-sided chapter notes]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{sidenotes}}
\ProcessOptions*\relax
\LoadClass[duplex]{sidenotes}
\endinput
