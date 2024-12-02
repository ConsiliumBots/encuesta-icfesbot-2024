// Step 1: Import the data
import excel "/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/hied_options/SNIES/Programas_20240913_nombres_corregidos_lista_encuesta.xlsx", firstrow clear

rename NOMBRE_INSTITUCIÓN nombre_institución
rename NOMBRE_DEL_PROGRAMA nombre_del_programa

// Step 2: Convert all text in "nombre_institucion" and "nombre_del_programa" to uppercase
replace nombre_institución = upper(nombre_institución)
replace nombre_del_programa = upper(nombre_del_programa)

// Step 3: Remove accents from "nombre_institucion" (both uppercase and lowercase)
replace nombre_institución = subinstr(nombre_institución, "Á", "A", .)
replace nombre_institución = subinstr(nombre_institución, "á", "A", .)
replace nombre_institución = subinstr(nombre_institución, "É", "E", .)
replace nombre_institución = subinstr(nombre_institución, "é", "E", .)
replace nombre_institución = subinstr(nombre_institución, "Í", "I", .)
replace nombre_institución = subinstr(nombre_institución, "í", "I", .)
replace nombre_institución = subinstr(nombre_institución, "Ó", "O", .)
replace nombre_institución = subinstr(nombre_institución, "ó", "O", .)
replace nombre_institución = subinstr(nombre_institución, "Ú", "U", .)
replace nombre_institución = subinstr(nombre_institución, "ú", "U", .)
replace nombre_institución = subinstr(nombre_institución, "Ñ", "Ñ", .)
replace nombre_institución = subinstr(nombre_institución, "ñ", "Ñ", .)

// Remove accents from "nombre_del_programa" (both uppercase and lowercase)
replace nombre_del_programa = subinstr(nombre_del_programa, "Á", "A", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "á", "A", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "É", "E", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "é", "E", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "Í", "I", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "í", "I", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "Ó", "O", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "ó", "O", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "Ú", "U", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "ú", "U", .) 
replace nombre_del_programa = subinstr(nombre_del_programa, "Ñ", "Ñ", .)
replace nombre_del_programa = subinstr(nombre_del_programa, "ñ", "Ñ", .)

// Step 4: Drop duplicates based on "nombre_institucion" and "nombre_del_programa"
duplicates drop nombre_institución nombre_del_programa, force

export excel "/Users/ignaciolepe/ConsiliumBots Dropbox/ConsiliumBots/Projects/Colombia/Icfesbot/2024/Data/Inputs/hied_options/SNIES/Programas_20240913_clean_lista_encuesta.xlsx", replace
