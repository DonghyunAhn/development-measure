/*-----------------------------------------------------------------------------------
Name: Sangyoon Park
Date: June 28 2022
This do file does : 
	Master do-file to run set of do-files
-----------------------------------------------------------------------------------*/
clear all
set matsize 10000
set maxvar 10000
set more off



/*-----------------------------------------------------------------------------------
			/* Set up */
-----------------------------------------------------------------------------------*/
*** Setting up working directories

	gl user "" // type in username
	if "${user}"=="" gl cdir = "" // type in the home directory you use


	gl raw_path = "$cdir/raw_data"		// path for raw data
	gl do_path = "$cdir/code"	// path for do file
	gl out_path = "$cdir/outputfile"	// path for stata output file
	gl table_path = "$cdir/writing/tables" 		// path for tables
	gl figure_path = "$cdir/writing/figures" 		// path for figures
	
	
*** Run set up program

	do "${do_path}/setup_program"
	
*** Run regression files

	do "${do_path}/regression_table1_github"
	
	do "${do_path}/regression_tables3_github"
