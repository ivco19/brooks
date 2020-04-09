# ---------------------------------------------------
# --------- Parametros de Inicializacion  -----------
# ---------------------------------------------------

nProc <- 250 # Numero de casos

# ---------------------------------------------------
# Algunas opciones para completar la tabla
# ---------------------------------------------------

nacionalidades <- c('Argentina', 'Brasil', 'Chile', 'Uruguay', 'Bolivia', 'Paraguay', 'Europa', 'USA') # Vector con las nacionalidades
direcciones    <- c('Calle1 Numero1', 'Calle2 Numero1', 'Calle3 Numero1', 'Calle4 Numero1', 'Calle5 Numero1', 'Calle6 Numero1') 
domicilios    <- c('Calle1 Numero1', 'Calle2 Numero1', 'Calle3 Numero1', 'Calle4 Numero1', 'Calle5 Numero1', 'Calle6 Numero1') 
centros    <- c('Hospital1', 'Hospital2','Hospital3', 'Hospital4','Hospital5', 'Hospital6') 
origenes <- c('Brasil', 'Chile', 'Uruguay', 'Bolivia', 'Paraguay', 'Europa', 'USA') # Vector con las nacionalidades
sinto          <- c('secreciones nasales', 'tos', 'fiebre', 'dificultad para respirar', 'dolor de garganta')
fechas_comienzo     <- 1:100

# ---------------------------------------------------
# ----------------- Creacion de la tabla ------------
# ---------------------------------------------------

Id_proc                     <- 1:nProc
Id_proc[]                   <- -99 
Id_pac                      <- 1:nProc
Id_pac[]                    <- -99 
genero                      <- 1:nProc
genero[]                    <- -99 
Edad                        <- 1:nProc
Edad[]                      <- -99 
Nacionalidad                <- 1:nProc
Nacionalidad[]              <- -99 
Residencia                  <- 1:nProc
Residencia[]                <- -99 
sintomatico                 <- 1:nProc
sintomatico[]               <- -99 
sintomas                    <- 1:nProc
sintomas[]                  <- -99 
Domicilio_Aislamiento       <- 1:nProc 
Domicilio_Aislamiento[]     <-  -99
Estado                      <- 1:nProc
Estado[]                    <- -99 
Centro_salud                <- 1:nProc
Centro_salud[]              <- -99 
Origen                      <- 1:nProc
Origen[]                    <- -99 
Fuente_de_infeccion         <- 1:nProc 
Fuente_de_infeccion[]       <-  -99
Fecha_comienzo_sintomas     <- 1:nProc
Fecha_comienzo_sintomas[]   <- -99 
Fecha_confirmacion_positivo <- 1:nProc
Fecha_confirmacion_positivo[]- -99 
Fecha_fallecimiento         <- 1:nProc
Fecha_fallecimiento[]       <- -99 
Fecha_alta                  <- 1:nProc
Fecha_alta[]                <- -99 

j = 0
i = 0
while(j < nProc){
  j = j+1
  i = i+1
# Nuevo caso sospechoso
#{{{
  Id_proc[j]      <- j # (números correlativos alcanza)
  Id_pac[j]       <- i # sample(1:150, size = nProc, replace = TRUE)
  genero[j]       <- sample(c('M', 'F'), size = 1, replace = TRUE)  
  Edad[j]         <- sample(1:80, size = 1, replace = TRUE)
  Nacionalidad[j] <- sample(nacionalidades, size = 1, 
                            replace = TRUE, 
                            prob = c(0.9, 0.014, 0.014, 0.014, 0.014, 0.014, 0.016, 0.014)) 
  Residencia[j]   <- sample(direcciones, size = 1, replace = TRUE)
  sintomatico[j]  <- sample(c('SI', 'NO'), size = 1, replace = TRUE)
  sintomas[j]     <- sample(sinto, size = 1, replace = TRUE)
  Domicilio_Aislamiento[j] <- sample(domicilios, size = 1, replace = TRUE) 

  Estado[j]       <- 'Sospechoso' # Todos empiezan como sospechosos?
#}}}

  if(runif(1) > 0.8){ # Probabilidad de que este infectado 
    # Nuevo caso Confirmado
    # Generamos una nueva entrada en la tabla, 
    # pero los datos del paciente tienen que coincidir
    #{{{
    j = j+1
    Id_proc[j]      <- j       
    Id_pac[j]       <- Id_pac[j-1]       
    genero[j]       <- genero[j-1]         
    Edad[j]         <- Edad[j-1]         
    Nacionalidad[j] <- Nacionalidad[j-1] 
    Residencia[j]   <- Residencia[j-1]   
    sintomatico[j]  <- sintomatico[j-1]  
    sintomas[j]     <- sintomas[j-1]     
    Domicilio_Aislamiento[j] <- Domicilio_Aislamiento[j-1]   

    Estado[j]       <- 'Activo' # Todos empiezan como sospechosos?
    Centro_salud[j] <- sample(centros, size = 1, replace = TRUE)
    Fuente_de_infeccion[j] <- sample(c('Caso importado', 'Contacto estrecho', 'Transmision local', 'Indefinido'), size = 1, replace = TRUE) 
    if(Fuente_de_infeccion[j] == 'Transmision local'){
      Origen[j] <- 'Argentina'
    } else {
      Origen[j]       <- sample(origenes, size = 1, replace = TRUE) 
    }
    Fecha_comienzo_sintomas[j]     <- sample(fechas_comienzo, size = 1, replace = TRUE)
    Fecha_confirmacion_positivo[j] <- Fecha_comienzo_sintomas[j] + sample(1:6, size = 1, replace = TRUE)
    
    #}}}
    if(runif(1) > 0.8){ # Probabilidad de que se muera
      # Generamos una nueva entrada en la tabla, 
      # pero los datos del paciente tienen que coincidir
      # Nuevo Fallecimiento
      #{{{
      j = j+1
      Id_proc[j]      <- j       
      Id_pac[j]       <- Id_pac[j-1]       
      genero[j]       <- genero[j-1]         
      Edad[j]         <- Edad[j-1]         
      Nacionalidad[j] <- Nacionalidad[j-1] 
      Residencia[j]   <- Residencia[j-1]   
      sintomatico[j]  <- sintomatico[j-1]  
      sintomas[j]     <- sintomas[j-1]     
      Domicilio_Aislamiento[j] <- Domicilio_Aislamiento[j-1]   

      Estado[j]       <- 'Fallecido' # Todos empiezan como sospechosos?
      Centro_salud[j] <- Centro_salud[j-1]
      Origen[j]       <- Origen[j-1]  
      Fuente_de_infeccion[j] <- Fuente_de_infeccion[j-1] 
      Fecha_comienzo_sintomas[j]     <- Fecha_comienzo_sintomas[j-1]
      Fecha_confirmacion_positivo[j] <- Fecha_confirmacion_positivo[j-1]
      Fecha_fallecimiento[j]         <- Fecha_comienzo_sintomas[j-1] + sample(10:20, size = 1, replace = TRUE)
      Fecha_alta[j]         <- -99
      #}}}
    } else {
      # Nuevo recuperado
      #{{{
      # Generamos una nueva entrada en la tabla, 
      # pero los datos del paciente tienen que coincidir
      j = j+1
      Id_proc[j]      <- j      
      Id_pac[j]       <- Id_pac[j-1]       
      genero[j]       <- genero[j-1]         
      Edad[j]         <- Edad[j-1]         
      Nacionalidad[j] <- Nacionalidad[j-1] 
      Residencia[j]   <- Residencia[j-1]   
      sintomatico[j]  <- sintomatico[j-1]  
      sintomas[j]     <- sintomas[j-1]     
      Domicilio_Aislamiento[j] <- Domicilio_Aislamiento[j-1]   

      Estado[j]       <- 'Recuperado' # Todos empiezan como sospechosos?
      Centro_salud[j] <- Centro_salud[j-1]
      Origen[j]       <- Origen[j-1]  
      Fuente_de_infeccion[j] <- Fuente_de_infeccion[j-1] 
      Fecha_comienzo_sintomas[j]     <- Fecha_comienzo_sintomas[j-1]
      Fecha_confirmacion_positivo[j] <- Fecha_confirmacion_positivo[j-1]
      Fecha_alta[j]   <- Fecha_confirmacion_positivo[j-1] + sample(10:20, size = 1, replace = TRUE)
      Fecha_fallecimiento[j]         <- -99
      #}}}
    }
  }
}

data <- data.frame(Id_proc, Id_pac, genero, Edad, Nacionalidad, Residencia, sintomatico, sintomas, Domicilio_Aislamiento, Estado, Centro_salud, Origen, Fuente_de_infeccion, Fecha_comienzo_sintomas, Fecha_confirmacion_positivo, Fecha_fallecimiento, Fecha_alta)

write.table(data, file = 'mock_data_covid19.csv', sep = ',', row.names = FALSE, quote = FALSE)

