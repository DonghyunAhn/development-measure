/*----------------------------------------------------------------
Date:  April 1 2021
This do file does:
	Imports and Processes North Korea Regional Data
-----------------------------------------------------------------*/

set more off
clear all
capture log close


 ** Tex Table notes		

	local notes_ols_kdd_viirs_grid \item Notes: This table reports OLS regression estimates. All specifications include province fixed effects, log of population in 2008 and log of land area. Standard errors are clustered at province level and reported in parentheses. * denotes statistical significance at 0.10, ** at 0.05, and *** at 0.01.			
	

/*-----------------------------------------------------------------------------------
			/* Grid level KDD Change */
-----------------------------------------------------------------------------------*/	

import excel "${raw_path}/nk_scores_0322_fourth_2.xlsx", sheet("grid_original") cellrange(A1:F32579) firstrow
rename y_x gridid
rename direc county_code
rename year2016 kddmean2016
rename year2017 kddmean2017
rename year2018 kddmean2018
rename year2019 kddmean2019

tempfile gridkdd
save `gridkdd'
clear

import excel "${raw_path}/NK_gird_NL_mean.xlsx", sheet("Sheet1") firstrow
rename NL16mean nlmean2016
rename NL19mean nlmean2019
tempfile gridnl
save `gridnl'
clear

import excel "${raw_path}/NK_grid_dummy.xlsx", sheet("Sheet2") firstrow
local sez "SEZ SEZ_agriculture SEZ_tourism SEZ_industry SEZ_export Mines Apitite Coal Copper Gold Graphite Iron Magnesite Molybdenum RareEarth Tungsten Uranium Zinc Tour_KimJongun Nuclear"
foreach y of local sez {
	replace `y' = 0 if `y' == .
}

tempfile gridsez
save`gridsez'
clear


import excel "${raw_path}/NK_gird_distance.xlsx", sheet("centroid_to_borders") firstrow

merge 1:1 gridid using `gridnl'
drop _merge

merge 1:1 gridid using `gridkdd'
drop _merge

merge 1:1 gridid using `gridsez'
drop _merge

tempfile grid_merge
save `grid_merge'
clear



import excel "${raw_path}/NKData_ver210108.xlsx", sheet("Data") firstrow case(lower)
drop if county_code == .

merge 1:m county_code using `grid_merge'
drop _merge


drop sido_dummy* kddsq* hm* pm* ldistance_* distance_*
sort county_code gridid
rename county_code county
gen grid = _n
reshape long kddmean nlmean, i(grid) j(year) string
gen lkddmean = log(kddmean+0.01)
gen lnlmean = log(nlmean+0.01)
gen yyear = real(year)
drop year
rename yyear year
keep if year >= 2015
keep if year == 2016 | year == 2019
egen std_nlmean_16 = std(nlmean) if year == 2016
egen std_nlmean_19 = std(nlmean) if year == 2019
gen std_nlmean = std_nlmean_16 if year == 2016
replace std_nlmean = std_nlmean_19 if year == 2019
bys grid: gen kddchange = kddmean[_n] - kddmean[_n-1] if year == 2019
bys grid: gen stdnlmeanchange = std_nlmean[_n] - std_nlmean[_n-1] if year == 2019
bys grid: gen lkddchange = lkddmean[_n] - lkddmean[_n-1] if year == 2019
bys grid: gen lnlmeanchange = lnlmean[_n] - lnlmean[_n-1] if year == 2019
keep if year == 2019
gen kddup = (kddchange > 0)
gen nlmeanup = (stdnlmeanchange > 0)
egen sum_pop2008 = sum(pop2008)
gen share_pop2008 = pop2008/sum_pop2008	
gen py_dummy = (sido_name == "Pyongyang")
encode sido_name, gen(province)
gen larea = log(area)
gen ldistance_border = log(Distance_border)
gen ldistance_city = log(Distance_city)
gen ldistance_port = log(Distance_port)
gen ldistance_py = log(Distance_Pyongyang)

local distance "ldistance_border ldistance_py ldistance_city ldistance_port"
local sez "SEZ_agriculture Tour_KimJongun SEZ_industry SEZ_export"
local dummy "chinaborder_dummy port_dummy city_dummy py_dummy"
local mines "Gold Coal Copper Iron Uranium"
*** Label 

	lab var ldistance_border " Log distance to NK-China and Russia border"
	lab var ldistance_port " Log distance to nearest major port"
	lab var ldistance_city " Log distance to nearest city"
	lab var ldistance_py " Log distance to Pyongyang"
	lab var chinaborder_dummy " Bordering China (dummy)"
	lab var port_dummy " Major seaport (dummy)"
	lab var city_dummy " Major city (dummy)"
	lab var py_dummy " Pyongyang (dummy)"	
	lab var sez_industry "Economic Development Zone - industrial complex"
	lab var sez_export "Economic Development Zone - export processing"
	lab var sez_agriculture "Economic Development Zone - agriculture project"
	lab var sez_tourism "Economic Development Zone - tourism project"
	lab var SEZ_industry "Economic Development Zone - industrial complex"
	lab var SEZ_export "Economic Development Zone - export processing"
	lab var SEZ_agriculture "Economic Development Zone - agriculture project"
	lab var SEZ_tourism "Economic Development Zone - tourism project"
	lab var Tour_KimJongun "Economic Development Zone - tourism project"	
	lab var Nuclear "Nuclear test site"
	local minetype "Gold Copper Coal Uranium Iron"
	foreach y of local minetype {
	lab var `y' "Mine site - `y'"
	}

	
*/


** Mixed
*** Setting
	loc numbers "& (1) & (2) & (3) & (4) \\ \midrule"
	loc reg_table cells(b(fmt(3) star) se(par fmt(3))) starlevels(* 0.10 ** 0.05 *** 0.01) ///
		stats(ymean N, fmt(2 0) ///
		labels("Mean of outcome variable" "Observations"))  ///
		label mlabels(none) collabels(none) nonotes nonumbers posthead("`numbers'") ///
		mgroups("$\Delta$ ln(siScore)" "$\Delta$ ln(NL)" "$\mathbbm{1} \{\Delta$ siScore $>$ 0\}" "$\mathbbm{1} \{\Delta$ NL $>$ 0\}", pattern(1 1 1 1) ///
		span prefix(\multicolumn{@span}{c}{) suffix(}) erepeat(\cmidrule(lr){@span})) ///
		indicate("Province FE=*.province") 
		

*** Estimation		
local outcome "lkddchange lnlmeanchange kddup nlmeanup"

	foreach y of local outcome {

		eststo: qui	reg `y' `distance' `sez' `mines' Nuclear i.province lpop2008 larea, robust cluster(province)
		qui summ `y'
		qui estadd scalar ymean = r(mean)
	}


** Table;
	loc colnum 4
	local caption Grid-Level Regression Estimates (2016-2019)
	local label ols_kdd_viirs
	local notes `notes_ols_kdd_viirs_grid'

head_foot, caption(`caption') label(`label') notes(`notes') columns(`colnum')

esttab  ///
using "${table_path}/mixed_kdd_viirs_grid.tex", replace ///
	keep(`distance' `sez' `mines' Nuclear) `reg_table' ///
	prehead("$header") postfoot("$footer") substitute("\_" "_")	

est clear	

































