///////////////////////////
/*
Este codigo crea las bases de contactos
para la encuesta de postulacion de carreras
en Colombia, enviada en noviembre de 2024. 
*/
///////////////////////////

// Dir
{
	global directorio "/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data"
}

// Inputs 
{
	import excel "$directorio/Inputs/students/base_inscritos_2024.xlsx", clear firstrow
}

// Data edit
{
	// Identificamos celulares inválidos
	gen cel = ustrregexra(estu_celular, "[^0-9]", "") // Quitar caracteres no numericos	
	
	destring cel, replace
	summ cel
	
	// Filter out numbers that do not start with '3'
	replace cel = . if substr(string(cel), 1, 1) != "3"

	// Filter out numbers that do not contain exactly 10 digits
	replace cel = . if cel < 1000000000 | cel >= 10000000000

	// Filter out numbers with all repeated digits (e.g., 1111111111)
	replace cel = . if regexm(string(cel), "^(.)\1{9}$")

	// Filter out numbers with repeated digits after the first two (e.g., 3011111111)
	replace cel = . if regexm(string(cel), "^3[0-9](\\1{7})$")
	
	// Drop invalid phone numbers
	drop if missing(cel) // 4,458 observations deleted
	
	// Agregamo código región.
	gen cel_final = "57" + string(cel, "%10.0f")
	drop cel
	rename cel_final cel
	
	destring cel, replace
	summ cel
	
	
	// Tageamos y dropeamos contactos duplicados
	duplicates tag estu_primernombre estu_segundonombre cel, gen(duplicado) // Contacto duplicado -> Mantenemos una de las copias
	bysort estu_primernombre estu_segundonombre cel: gen nro_duplicado = _n if duplicado >0
	drop if nro_duplicado > 1 & nro_duplicado != . // 2,587 observations deleted
	drop duplicado nro_duplicado
	
	// Tageamos y dropeamos personas distintas con el mismo celular
	duplicates tag cel, gen(duplicado) // celular duplicado -> borramos todas las personas con el mismo celular
	drop if duplicado != 0 // 77,850 observations deleted
	drop duplicado
	
	sort estu_primernombre estu_segundonombre cel
	count // 488,828 observations
	
	// Arreglo manual de nombres con error
	sort estu_segundonombre
	replace estu_segundonombre = "MARIANA" if estu_primernombre == "1025531895"
	replace estu_primernombre = "ALICE" if estu_primernombre == "1025531895"
	
	// Formateo nombre
	// Replace accented characters with non-accented equivalents
	replace estu_primernombre = subinstr(estu_primernombre, "á", "a", .)
	replace estu_primernombre = subinstr(estu_primernombre, "é", "e", .)
	replace estu_primernombre = subinstr(estu_primernombre, "í", "i", .)
	replace estu_primernombre = subinstr(estu_primernombre, "ó", "o", .)
	replace estu_primernombre = subinstr(estu_primernombre, "ú", "u", .)
	replace estu_primernombre = subinstr(estu_primernombre, "ñ", "n", .)
	replace estu_primernombre = subinstr(estu_primernombre, "ü", "u", .)

	// Uppercase accented characters
	replace estu_primernombre = subinstr(estu_primernombre, "Á", "A", .)
	replace estu_primernombre = subinstr(estu_primernombre, "É", "E", .)
	replace estu_primernombre = subinstr(estu_primernombre, "Í", "I", .)
	replace estu_primernombre = subinstr(estu_primernombre, "Ó", "O", .)
	replace estu_primernombre = subinstr(estu_primernombre, "Ú", "U", .)
	replace estu_primernombre = subinstr(estu_primernombre, "Ñ", "N", .)
	replace estu_primernombre = subinstr(estu_primernombre, "Ü", "U", .)

	replace estu_primernombre = proper(estu_primernombre)
	
	// Renombrar variable celular
	rename cel cellphone
	
	// borrar numeros con digitos repetidos
	// todos los que empiezan en 3
	// solo 10 digitos
	// agregar 57 al inicio del numero
	// duplicates tag
	// drop if duplicated !=0
}

// Estratificacion
{			
	preserve
	// set semilla replicacion
	set seed 6112024 
	
	// Dropear departamentos falsos
	drop if estu_cod_reside_depto == 99999 | estu_cod_reside_depto == . 
	
	// Grupos de estratificación: departamento
	sort estu_cod_reside_depto
	sample 41, by(estu_cod_reside_depto)
	by estu_cod_reside_depto: count

	count
	
	tempfile sample_a_encuestar
	save `sample_a_encuestar', replace
	restore

	merge 1:1 cellphone using `sample_a_encuestar'
	gen estudiante_a_encuestar = 1 if _merge == 3
	drop _merge
	
	// Investigar aleatorizacion.                                    
	// Estrateficazion geografica.
	// Muestra 200k	
}


// Output
{			
	// muestra completa (encuestados y no encuestados)
	export delimited "$directorio/Outputs/students/base_procesada_2024.csv", replace
			
	// Mantener variables relevantes 
	keep cellphone estu_primernombre estudiante_a_encuestar
	
	// Muestra a encuestar
	keep if estudiante_a_encuestar == 1
	drop estudiante_a_encuestar
	
	// Crear indicador de la muestra completa
	gen id = _n
			
	// Muestra a encuestar por partes
	// Step 1: Generate a grouping variable that divides the dataset into 10 equal parts
	gen group = ceil(_n / ( _N / 10))
	
	rename cellphone phone
	rename estu_primernombre name
	order id phone name group
		
	// Muestra a encuestar completa
	export delimited "$directorio/Outputs/envio/base_envio_2024_completa.csv", replace

	drop id

	// Step 2: Loop over each group and save it as a separate file
	forvalues i = 1/10 {
		preserve
		keep if group == `i'
		drop group
		
		// Cargar observacion Mauro e Ignacio para testear envios
		{
		   append using "$directorio/Inputs/students/test_Mauricio_Ignacio.dta"
		}
		
		// Crear indicador del sample
		gen id = _n
		
		keep id phone name
		order id phone name
		
		export delimited "$directorio/Outputs/envio/base_envio_2024_parte`i'.csv", replace
		save "$directorio/Outputs/envio/base_envio_2024_parte`i'.dta", replace
		restore
	}
	
	// Appendeamos todas las bases para generar links unicos en qualtrics
	use "$directorio/Outputs/envio/base_envio_2024_parte1.dta", clear
		
	forvalues i = 2/10 {
		append using "$directorio/Outputs/envio/base_envio_2024_parte`i'.dta"
	}
		 	
	gen id_unico = _n * 10 + 12112024
	rename id_unico External_data_reference
	rename name First_Name 
	rename phone Phone_number
	
	gen Last_name = ""
	gen Email = ""
	gen Language = "Spanish"
	
	keep First_Name Last_name Email External_data_reference Phone_number Language
	order First_Name Last_name Email External_data_reference Phone_number Language
	
	export delimited "$directorio/Outputs/envio/listado_de_conctactos_qualtrics_para_subir.csv", replace 
	rename External_data_reference externaldatareference
	rename Phone_number phone
	save "$directorio/Outputs/envio/listado_de_conctactos_qualtrics_para_subir.dta", replace
	
	// Cross-walk link a telefono 
	import delimited "$directorio/Outputs/envio/listado_de_contacto_qualtrics_descargado.csv", clear
	
	merge 1:1 externaldatareference using "$directorio/Outputs/envio/listado_de_conctactos_qualtrics_para_subir.dta"
	keep phone link
	
	// recuperamos links de testing mauro e ignacio
	preserve
	keep if phone < 570000000000
	gen name = "Ignacio" if phone == 56975815720
	replace name = "Mauro" if phone == 56985051369
	bysort phone: gen test = _n
	save "$directorio/Outputs/envio/link_testing.dta", replace
	restore
	
	drop if phone < 570000000000
	save "$directorio/Outputs/envio/crosswalk_phone_link.dta", replace
	
	// imputar link a cada una de las 10 partes de la encuesta	
	forvalues i = 1/10 {
		use using "$directorio/Outputs/envio/base_envio_2024_parte`i'.dta", clear
		merge 1:1 phone using "$directorio/Outputs/envio/crosswalk_phone_link.dta"
		keep if _merge == 3
		drop _merge
		
		append using "$directorio/Outputs/envio/link_testing.dta" 
		keep if test == `i' | test == .
		drop test
		rename phone number
		
		drop id
		gen id = _n
		order id number name link
		
		gen link_unique = ""
		// Extract the part of the link following "CGC_"
		replace link_unique = regexs(1) if regexm(link, "CGC_(.*)")
		replace link = link_unique
		drop link_unique
		
		save "$directorio/Outputs/envio/base_envio_2024_parte`i'_final.dta", replace
		export delimited "$directorio/Outputs/envio/base_envio_2024_parte`i'_final.csv", replace
	}
	
	// Juntar las 10 partes de las encuestas con link
	use "$directorio/Outputs/envio/base_envio_2024_parte1_final.dta", clear
	
	forvalues i = 2/10 {
		append using "$directorio/Outputs/envio/base_envio_2024_parte`i'_final.dta"
	}
	
	drop if number == 56975815720
	drop if number == 56985051369
	save "$directorio/Outputs/envio/base_envio_2024_completa_final.dta", replace
	
	// Merge con encuestados que no les llegó link correcto
	import delimited "$directorio/Outputs/envio/numeros_qualtrics_icfesbot.csv", clear
	count
	keep number
	save "$directorio/Outputs/envio/numeros_qualtrics_icfesbot.dta", replace
	
	merge 1:1 number using "$directorio/Outputs/envio/base_envio_2024_completa_final.dta"
	keep if _merge == 3
	drop _merge
	order id number name link
	export delimited "$directorio/Outputs/envio/lista_de_reenvio.csv", replace 
	count 
}
