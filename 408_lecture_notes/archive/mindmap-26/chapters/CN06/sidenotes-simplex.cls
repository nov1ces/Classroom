% Explicit single-sided entry point. See LICENSE.
\NeedsTeXFormat{LaTeX2e}[2022/06/01]
\ProvidesClass{sidenotes-simplex}[2026/10/25 v1.1 Single-sided chapter notes]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{sidenotes}}
\ProcessOptions*\relax
\LoadClass[simplex]{sidenotes}
\endinput
