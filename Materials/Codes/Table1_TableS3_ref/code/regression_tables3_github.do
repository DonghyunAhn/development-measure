/*-----------------------------------------------------------------------------------
Name: Sangyoon Park
Date: June 28 2022
This do file does : 
	Create regression table
-----------------------------------------------------------------------------------*/

clear

/*-----------------------------------------------------------------------------------
			 Import data
-----------------------------------------------------------------------------------*/


import excel "${raw_path}/Regression_cluster_v4_ensemble.xlsx", sheet("original") firstrow case(l)

/*-----------------------------------------------------------------------------------
			 Setup data
-----------------------------------------------------------------------------------*/

*** Keep only year 2019

rename y_x grid_id
sort grid_id year
bys grid_id: keep if _n == 4
replace year = 2019 if year == .

*** Generate ranking of POG

gen pog_rank = .
replace pog_rank = 8 if inlist(clusternum, 1,2,3,4,6)
replace pog_rank = 7 if inlist(clusternum, 0,7)
replace pog_rank = 6 if inlist(clusternum, 5,8,9,10)
replace pog_rank = 5 if inlist(clusternum, 14,15,16,20)
replace pog_rank = 4 if inlist(clusternum, 17,21)
replace pog_rank = 3 if inlist(clusternum, 13,18)
replace pog_rank = 2 if inlist(clusternum, 11,12)
replace pog_rank = 1 if inlist(clusternum, 19)
replace pog_rank = 0 if inlist(clusternum, 22)

gen pog_urban = inrange(clusternum,0,10)
gen pog_rural = inrange(clusternum,11,22)

gen pog_urban_rank = .
replace pog_urban_rank = 3 if inlist(clusternum, 1,2,3,4,6)
replace pog_urban_rank = 2 if inlist(clusternum, 0,7)
replace pog_urban_rank = 1 if inlist(clusternum, 5,8,9,10)

gen pog_rural_rank = .
replace pog_rural_rank = 5 if inlist(clusternum, 14,15,16,20)
replace pog_rural_rank = 4 if inlist(clusternum, 17,21)
replace pog_rural_rank = 3 if inlist(clusternum, 13,18)
replace pog_rural_rank = 2 if inlist(clusternum, 11,12)
replace pog_rural_rank = 1 if inlist(clusternum, 19)
replace pog_rural_rank = 0 if inlist(clusternum, 22)

/*-----------------------------------------------------------------------------------
			 Generate variable
-----------------------------------------------------------------------------------*/

local var "lulcused lulcagri lulcforest roadarea buildingarea"

foreach y of local var {
	gen `y'2 = `y'^2
	}
	
/*-----------------------------------------------------------------------------------
			 Label variable
-----------------------------------------------------------------------------------*/	
	
lab var lulcagri "Agricultural land"
lab var lulcforest "Forest land"
lab var roadarea "Road"
lab var buildingarea "Building"
lab var lulcused "Used land"
lab var lulcgrass "Grass land"
lab var lulcwet "Wet land"
lab var lulcbarren "Barren land"
lab var lulcwater "Water"	
	
local lulc "lulcused lulcagri lulcforest lulcgrass lulcbarren lulcwater"

/*-----------------------------------------------------------------------------------
			 Regression
-----------------------------------------------------------------------------------*/	
local notes_cluster \item Notes: This table regression coefficients using the ranking of cluster orderings ///
as the outcome variable. ///
	Each unit of observation is at the grid level. Standard errors are clustered by POG cluster ///
	and reported in parentheses. * denotes statistical significance at 0.10, ** at 0.05, and *** at 0.01. 		


***** With cluster 22	
** Setting
	loc titles "& \multicolumn{3}{c}{All clusters} & \multicolumn{3}{c}{Within urban} & \multicolumn{3}{c}{Within rural}\\ \cmidrule(lr){2-4} \cmidrule(lr){5-7} \cmidrule(lr){8-10}" 
	loc numbers "& (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) & (9) \\ \midrule"
	loc reg_table cells(b(fmt(3) star) se(par fmt(3))) starlevels(* 0.10 ** 0.05 *** 0.01) ///
		stats(r2 N, fmt(2 0) ///
		labels("R-squared" "Observations"))  ///
		label mlabels(none) collabels(none) nonotes nonumbers posthead("`titles'" "`numbers'") ///
		mgroups("Ranking of clusters", pattern(1 0 0 0 0 0 0 0 0) ///
		span prefix(\multicolumn{@span}{c}{) suffix(}) erepeat(\cmidrule(lr){@span}))

** Estimation	
	eststo: qui reg pog_rank `lulc', robust cluster(cluster)
	eststo: qui reg pog_rank buildingarea roadarea, robust cluster(cluster)
	eststo: qui reg pog_rank `lulc' buildingarea roadarea, robust cluster(cluster)	
	
	eststo: qui reg pog_urban_rank `lulc' if pog_urban == 1, robust cluster(cluster)
	eststo: qui reg pog_urban_rank buildingarea roadarea if pog_urban == 1, robust cluster(cluster)
	eststo: qui reg pog_urban_rank `lulc' buildingarea roadarea if pog_urban == 1, robust cluster(cluster)	
	
	eststo: qui reg pog_rural_rank `lulc' if pog_rural == 1, robust cluster(cluster)
	eststo: qui reg pog_rural_rank buildingarea roadarea if pog_rural == 1, robust cluster(cluster)
	eststo: qui reg pog_rural_rank `lulc' buildingarea roadarea if pog_rural == 1, robust cluster(cluster)		

** Table
	loc colnum 9
	local caption Regression: Cluster ordering and visual features of grids
	local label regression_clusterordering
	local notes `notes_cluster'

head_foot, caption(`caption') label(`label') notes(`notes') columns(`colnum')

esttab  ///
using "${table_path}/reg_clusterordering_with22.tex", replace ///
	keep(`lulc' buildingarea roadarea) `reg_table' ///
	prehead("$header") postfoot("$footer") substitute("\_" "_")

est clear	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	
