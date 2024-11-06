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
	replace cel = "." if substr(cel, 1, 1) != "3" 	  // Quitar numeros que no comienzan con 3
	replace cel = "." if length(cel) > 10			  // Quitar numeros que no contengan 10 digitos
	replace cel = "." if regexm(cel, "^(.)\1{9}$")      // Quitar numeros falsos (digitos repetidos, e.g 1111111111)
	replace cel = "." if regexm(cel, "^3[0-9](\\1{7})$") // Quitar numeros falsos (digitos repetidos, e.g 3011111111, 31..., 32....)
	
	// Chequeamos cantidad de celulares invalidos
	drop if cel == "." // 4,429 observations deleted
	
	// Agregamo código región.
	replace cel = "57" + cel
	
	// Tageamos y dropeamos contactos duplicados
	duplicates tag estu_primernombre estu_segundonombre cel, gen(duplicado) // Contacto duplicado -> Mantenemos una de las copias
	bysort estu_primernombre estu_segundonombre cel: gen nro_duplicado = _n if duplicado >0
	drop if nro_duplicado > 1 & nro_duplicado != . // 2,587 observations deleted
	drop duplicado nro_duplicado
	
	// Tageamos y dropeamos personas distintas con el mismo celular
	duplicates tag cel, gen(duplicado) // celular duplicado -> borramos todas las personas con el mismo celular
	drop if duplicado != 0 // 77,853 observations deleted
	drop duplicado
	
	sort estu_primernombre estu_segundonombre cel
	count // 488,854 observations
	
	destring cel, replace
	summ cel
	
	// Arreglo manual de nombres con error
	sort estu_segundonombre
	replace estu_segundonombre = "MARIANA" if estu_primernombre == "1025531895"
	replace estu_primernombre = "ALICE" if estu_primernombre == "1025531895"
	
	// Formateo nombre
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
	
	order id cellphone estu_primernombre group
		
	// Muestra a encuestar completa
	export delimited "$directorio/Outputs/envio/base_envio_2024_completa.csv", replace

	drop id

	// Step 2: Loop over each group and save it as a separate file
	forvalues i = 1/10 {
		preserve
		keep if group == `i'
		drop group
		
		// Cargar observacion Mauro
		{
		   append using "$directorio/Inputs/students/test_Mauricio.dta"
		}
		
		// Crear indicador del sample
		gen id = _n
		
		order id cellphone estu_primernombre
		
		export delimited "$directorio/Outputs/envio/base_envio_2024_parte`i'.csv", replace
		restore
	}
	
	// Una vez generadas las bases se renombra "estu_primernombre" con "1" para todas las bases
}
