CREATE DATABASE  IF NOT EXISTS `capired` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `capired`;
-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: capired
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_log`
--

DROP TABLE IF EXISTS `activity_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `details` text,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `activity_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `recurso_operativo` (`id_codigo_consumidor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_log`
--

LOCK TABLES `activity_log` WRITE;
/*!40000 ALTER TABLE `activity_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asignacion`
--

DROP TABLE IF EXISTS `asignacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asignacion` (
  `id_asignacion` int NOT NULL AUTO_INCREMENT,
  `asignacion_cedula` varchar(45) DEFAULT NULL,
  `asignacion_nombre` varchar(45) DEFAULT NULL,
  `asignacion_fecha` date DEFAULT NULL,
  `asignacion_cargo` varchar(45) DEFAULT NULL,
  `asignacion_adaptador_mandril` varchar(45) DEFAULT NULL,
  `asignacion_alicate` varchar(45) DEFAULT NULL,
  `asignacion_barra_45cm` varchar(45) DEFAULT NULL,
  `asignacion_bisturi_metalico` varchar(45) DEFAULT NULL,
  `asignacion_broca_3/8` varchar(45) DEFAULT NULL,
  `asignacion_broca_3/8/6_ran` varchar(45) DEFAULT NULL,
  `asignacion_broca_1/2/6_ran` varchar(45) DEFAULT NULL,
  `asignacion_broca_metal/madera_1/4` varchar(45) DEFAULT NULL,
  `asignacion_broca_metal/madera_3/8` varchar(45) DEFAULT NULL,
  `asignacion_broca_metal/madera_5/16` varchar(45) DEFAULT NULL,
  `asignacion_caja_de_herramientas` varchar(45) DEFAULT NULL,
  `asignacion_cajon_rojo` varchar(45) DEFAULT NULL,
  `asignacion_cinta_de_senal` varchar(45) DEFAULT NULL,
  `asignacion_cono_retractil` varchar(45) DEFAULT NULL,
  `asignacion_cortafrio` varchar(45) DEFAULT NULL,
  `asignacion_destor_de_estrella` varchar(45) DEFAULT NULL,
  `asignacion_destor_de_pala` varchar(45) DEFAULT NULL,
  `asignacion_destor_tester` varchar(45) DEFAULT NULL,
  `asignacion_espatula` varchar(45) DEFAULT NULL,
  `asignacion_exten_de_corr_10_mts` varchar(45) DEFAULT NULL,
  `asignacion_llave_locking_male` varchar(45) DEFAULT NULL,
  `asignacion_llave_reliance` varchar(45) DEFAULT NULL,
  `asignacion_llave_torque_rg_11` varchar(45) DEFAULT NULL,
  `asignacion_llave_torque_rg_6` varchar(45) DEFAULT NULL,
  `asignacion_llaves_mandril` varchar(45) DEFAULT NULL,
  `asignacion_mandril_para_taladro` varchar(45) DEFAULT NULL,
  `asignacion_martillo_de_una` varchar(45) DEFAULT NULL,
  `asignacion_multimetro` varchar(45) DEFAULT NULL,
  `asignacion_pelacable_rg_6y_rg_11` varchar(45) DEFAULT NULL,
  `asignacion_pinza_de_punta` varchar(45) DEFAULT NULL,
  `asignacion_pistola_de_silicona` varchar(45) DEFAULT NULL,
  `asignacion_planillero` varchar(45) DEFAULT NULL,
  `asignacion_ponchadora_rg_6_y_rg_11` varchar(45) DEFAULT NULL,
  `asignacion_ponchadora_rj_45_y_rj11` varchar(45) DEFAULT NULL,
  `asignacion_probador_de_tonos` varchar(45) DEFAULT NULL,
  `asignacion_probador_de_tonos_utp` varchar(45) DEFAULT NULL,
  `asignacion_puntas_para_multimetro` varchar(45) DEFAULT NULL,
  `asignacion_sonda_metalica` varchar(45) DEFAULT NULL,
  `asignacion_tacos_de_madera` varchar(45) DEFAULT NULL,
  `asignacion_taladro_percutor` varchar(45) DEFAULT NULL,
  `asignacion_telefono_de_pruebas` varchar(45) DEFAULT NULL,
  `asignacion_power_miter` varchar(45) DEFAULT NULL,
  `asignacion_bfl_laser` varchar(45) DEFAULT NULL,
  `asignacion_cortadora` varchar(45) DEFAULT NULL,
  `asignacion_stripper_fibra` varchar(45) DEFAULT NULL,
  `asignacion_pelachaqueta` varchar(45) DEFAULT NULL,
 
  `asignacion_estado` varchar(45) DEFAULT NULL,
  `id_codigo_consumidor` int DEFAULT NULL,
  PRIMARY KEY (`id_asignacion`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asignacion`
--

LOCK TABLES `asignacion` WRITE;
/*!40000 ALTER TABLE `asignacion` DISABLE KEYS */;
INSERT INTO `asignacion` VALUES (3,NULL,NULL,'2025-02-25','TECNICO','1','1','2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'4',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1',100),(4,NULL,NULL,'2025-02-07','TECNICO','1','1','0',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1',200),(5,NULL,NULL,'2025-02-13','ANALISTA','1','1','2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'4',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1',100),(6,NULL,NULL,'2025-02-24','ANALISTA','1','1','2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'4',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1',101);
/*!40000 ALTER TABLE `asignacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `herramienta`
--

DROP TABLE IF EXISTS `herramienta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `herramienta` (
  `idherramienta` int NOT NULL AUTO_INCREMENT,
  `herramienta_descripcion` varchar(45) DEFAULT NULL,
  `herramienta_valor` varchar(45) DEFAULT NULL,
  `herramienta_fechacompra` date DEFAULT NULL,
  `herramienta_cantidad` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idherramienta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `herramienta`
--

LOCK TABLES `herramienta` WRITE;
/*!40000 ALTER TABLE `herramienta` DISABLE KEYS */;
/*!40000 ALTER TABLE `herramienta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preoperacional`
--

DROP TABLE IF EXISTS `preoperacional`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preoperacional` (
  `id_preoperacional` int NOT NULL AUTO_INCREMENT,
  `centro_de_trabajo` varchar(255) DEFAULT NULL,
  `ciudad` varchar(255) DEFAULT NULL,
  `supervisor` varchar(255) DEFAULT NULL,
  `vehiculo_asistio_operacion` varchar(255) DEFAULT NULL,
  `tipo_vehiculo` varchar(255) DEFAULT NULL,
  `placa_vehiculo` varchar(255) DEFAULT NULL,
  `modelo_vehiculo` varchar(255) DEFAULT NULL,
  `marca_vehiculo` varchar(255) DEFAULT NULL,
  `licencia_conduccion` varchar(255) DEFAULT NULL,
  `fecha_vencimiento_licencia` date DEFAULT NULL,
  `fecha_vencimiento_soat` date DEFAULT NULL,
  `fecha_vencimiento_tecnomecanica` date DEFAULT NULL,
  `estado_espejos` varchar(255) DEFAULT NULL,
  `bocina_pito` varchar(255) DEFAULT NULL,
  `frenos` varchar(255) DEFAULT NULL,
  `encendido` varchar(255) DEFAULT NULL,
  `estado_bateria` varchar(255) DEFAULT NULL,
  `estado_amortiguadores` varchar(255) DEFAULT NULL,
  `estado_llantas` varchar(255) DEFAULT NULL,
  `kilometraje_actual` int DEFAULT NULL,
  `luces_altas_bajas` varchar(255) DEFAULT NULL,
  `direccionales_delanteras_traseras` varchar(255) DEFAULT NULL,
  `elementos_prevencion_seguridad_vial_casco` varchar(255) DEFAULT NULL,
  `casco_certificado` varchar(255) DEFAULT NULL,
  `casco_identificado` varchar(255) DEFAULT NULL,
  `estado_guantes` varchar(255) DEFAULT NULL,
  `estado_rodilleras` varchar(255) DEFAULT NULL,
  `impermeable` varchar(255) DEFAULT NULL,
  `observaciones` text,
  `estado_fisico_vehiculo_espejos` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_bocina_pito` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_frenos` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_encendido` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_bateria` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_amortiguadores` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_llantas` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_luces_altas` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_luces_bajas` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_direccionales_delanteras` varchar(255) DEFAULT NULL,
  `estado_fisico_vehiculo_direccionales_traseras` varchar(255) DEFAULT NULL,
  `elementos_prevencion_seguridad_vial_guantes` varchar(255) DEFAULT NULL,
  `elementos_prevencion_seguridad_vial_rodilleras` varchar(255) DEFAULT NULL,
  `elementos_prevencion_seguridad_vial_coderas` varchar(255) DEFAULT NULL,
  `elementos_prevencion_seguridad_vial_impermeable` varchar(255) DEFAULT NULL,
  `casco_identificado_placa` varchar(255) DEFAULT NULL,
  `id_codigo_consumidor` int DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `preoperacionalcol` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_preoperacional`),
  KEY `id_codigo_idx` (`id_codigo_consumidor`),
  CONSTRAINT `id_codigo_consumidor` FOREIGN KEY (`id_codigo_consumidor`) REFERENCES `recurso_operativo` (`id_codigo_consumidor`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preoperacional`
--

LOCK TABLES `preoperacional` WRITE;
/*!40000 ALTER TABLE `preoperacional` DISABLE KEYS */;
/*!40000 ALTER TABLE `preoperacional` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recurso_operativo`
--

DROP TABLE IF EXISTS `recurso_operativo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recurso_operativo` (
  `id_codigo_consumidor` int NOT NULL AUTO_INCREMENT,
  `recurso_operativo_cedula` varchar(20) NOT NULL,
  `recurso_operativo_password` varchar(255) NOT NULL,
  `id_roles` int NOT NULL,
  `estado` varchar(45) DEFAULT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  `cargo` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_codigo_consumidor`),
  UNIQUE KEY `recurso_operativo_cedula` (`recurso_operativo_cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recurso_operativo`
--

LOCK TABLES `recurso_operativo` WRITE;
/*!40000 ALTER TABLE `recurso_operativo` DISABLE KEYS */;
INSERT INTO `recurso_operativo` VALUES (1,'80833959','$2b$12$MoyoExdL4245dug3AxYnSukBeAHOrWSzQ1wgvWCOOy23SdTXJfv.q',1,'Activo','VICTOR ALFONSO NARANJO SIERRA','DESARROLLADOR'),(7,'1000954206','$2b$12$0pPWeQ0BZpd7II9uaU7wMuIuW/KqI8umRJFwQHO168uT/JqiBIS9e',2,'Activo','DIANA SOSA','ANALISTA'),(9,'123456789','$2b$12$lmSRIynNj8q3RBNF2am14eBOCua9QjVPAb5gbzifB4mYKzXhKzHpO',5,'Activo','FELIPE SANCHEZ','ANALISTA');
/*!40000 ALTER TABLE `recurso_operativo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `rol_descripcion` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'administrativo'),(2,'tecnicos'),(3,'operativo'),(4,'contabilidad'),(5,'logistica');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_roles` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_roles`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'administrativo'),(2,'tecnicos'),(3,'operativo'),(4,'contabilidad'),(5,'logistica');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rotacion_equipos_libres`
--

DROP TABLE IF EXISTS `rotacion_equipos_libres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rotacion_equipos_libres` (
  `id_rotacion_equipos_libres` int NOT NULL AUTO_INCREMENT,
  `rotacion_equipos_libres_serial_rr` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_cedula` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_nombre` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_tipo_bodega` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_código_tercero` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_elemento` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_familia` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_lote` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_serial` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_fecha_ultimo_mvto` date DEFAULT NULL,
  `rotacion_equipos_libres_dias_ultimo_mvto` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_carpeta` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_supervisor` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_mes` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_observacion` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_valor` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_reunion` varchar(45) DEFAULT NULL,
  `rotacion_equipos_libres_estado_2` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_rotacion_equipos_libres`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rotacion_equipos_libres`
--

LOCK TABLES `rotacion_equipos_libres` WRITE;
/*!40000 ALTER TABLE `rotacion_equipos_libres` DISABLE KEYS */;
INSERT INTO `rotacion_equipos_libres` VALUES (1,'GZ24040672913397','1014216655','JULIAN CAMILO MARTIN MARTINEZ','MOVIL','4072582','DECO SEI800CCOA-U V4 ATV 4K OTT SEIR','ANDROID_TV','VALORADO','GZ24040672913397','2025-01-22',NULL,'FTTH INSTALACIONES','MAURICIO MUÑOZ','05. Enero-2025','1. MAYOR A 10 DIAS','150000','2025-01-21','CONSUMIDO');
/*!40000 ALTER TABLE `rotacion_equipos_libres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suministros`
--

DROP TABLE IF EXISTS `suministros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suministros` (
  `id_suministros` int NOT NULL AUTO_INCREMENT,
  `suministros_codigo` varchar(45) DEFAULT NULL,
  `suministros_descripcion` varchar(45) DEFAULT NULL,
  `suministros_unidad_medida` varchar(45) DEFAULT NULL,
  `suministros_familia` varchar(45) DEFAULT NULL,
  `suministros_cliente` varchar(45) DEFAULT NULL,
  `suministros_tipo` varchar(45) DEFAULT NULL,
  `suministros_estado` varchar(45) DEFAULT NULL,
  `suministros_requiere_serial` varchar(45) DEFAULT NULL,
  `suministros_serial` varchar(45) DEFAULT NULL,
  `suministros_costo_unitario` int DEFAULT NULL,
  `suministros_cantidad` int DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_suministros`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suministros`
--

LOCK TABLES `suministros` WRITE;
/*!40000 ALTER TABLE `suministros` DISABLE KEYS */;
INSERT INTO `suministros` VALUES (1,'32131','utp','mts','cables','claro',NULL,NULL,'si',NULL,12356,10000,'2025-02-23 20:14:18'),(2,'987654','fibra 100 ','1','fibras','zte',NULL,NULL,'no',NULL,4568798,500,'2025-02-23 20:19:11'),(3,'32123','32131','0','cables','claro',NULL,NULL,'si',NULL,12356,10000,'2025-02-23 20:56:30'),(4,'987654','fibra 100 ','1','cables','claro',NULL,NULL,'si',NULL,4568798,10000,'2025-02-23 20:58:24'),(5,'32131','utp','3','fibras','DICO',NULL,NULL,'si',NULL,12356,10000,'2025-02-23 20:58:48'),(6,'CD5549','NACLAJES','3','HERRAJE','claro',NULL,NULL,'si',NULL,4568798,2000,'2025-02-24 07:13:26');
/*!40000 ALTER TABLE `suministros` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `idusuarios` int NOT NULL AUTO_INCREMENT,
  `usuario_nombre` varchar(45) DEFAULT NULL,
  `usuario_cedula` int DEFAULT NULL,
  `usuario_contraseña` int DEFAULT NULL,
  PRIMARY KEY (`idusuarios`),
  UNIQUE KEY `idusuarios_UNIQUE` (`idusuarios`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'vnaranjos',80833959,7885);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-02 19:43:31
