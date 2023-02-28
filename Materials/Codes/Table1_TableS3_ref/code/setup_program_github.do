/*-----------------------------------------------------------------------------------
Name: Sangyoon Park
Date: June 28 2022
This do file does : 
	Set up programs
-----------------------------------------------------------------------------------*/
clear all
set matsize 10000
set maxvar 10000
set more off
capture log close



/*-----------------------------------------------------------------------------------
			 Set up
-----------------------------------------------------------------------------------*/
*** Set up program
 ** Number Format
	capture program drop autoformat
	program define autoformat

	if int(`1')==`1' global format "%12.0f"
	else if abs(`1')>10 global format "%9.1f"
	else if abs(`1')>1 global format "%9.2f"
	else if abs(`1')>.1 global format "%9.3f"
	else if abs(`1')>.01 global format "%9.3f"
	else if abs(`1')>.001 global format "%9.3f"
	else if abs(`1')>.0001 global format "%9.4f"
	else if abs(`1')<.00001 global format "%9.5f"

	end
	
 ** Tex Table format
  	capture program drop head_foot
	program define head_foot

	syntax, [caption(str)] [label(str)] [notes(str)] [size(str)] [columns(str)] [sideways] [long]

	local estimates=r(names)
	if "`columns'"=="" local columns:word count `estimates'
	if "`sideways'"=="sideways" local table sidewaystable
	if "`long'"=="long" local table longtable
	else local table table
	local col = `columns'+1

	global header \begin{`table'}[ht!] \footnotesize \begin{center}
		if "`size'"!="" global header $header \begin{`size'}
		if "`caption'"!="" global header $header \caption{`caption'\label{table:`label'}} 
		global header $header  ///
		\begin{adjustbox}{max width=\textwidth} ///
		\begin{threeparttable} ///
		\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi} 
		global header $header ///
		\begin{tabular}{l*{`columns'}{c}}\toprule[1.5pt]

	global header_mid \tabularnewline

	global panel_title \multicolumn{`col'}{l}{Panel}\tabularnewline \midrule

	global footer_mid \midrule 
	global footer \bottomrule[1.2pt] ///
		\end{tabular} 
		if "`notes'"!="" {
			global footer $footer \begin{tablenotes}[flushleft] ///
			`notes' ///
			\end{tablenotes} 
			}
		global footer $footer \end{threeparttable}\end{adjustbox}
		if "`size'"!="" global footer $footer \end{`size'}
		global footer $footer \end{center} \end{`table'} 	
	end


	