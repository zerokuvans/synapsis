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
  `asignacion_arnes` varchar(45) DEFAULT NULL,
  `asignacion_eslinga` varchar(45) DEFAULT NULL,
  `asignacion_mosqueton` varchar(45) DEFAULT NULL,
  `asignacion_pretales` varchar(45) DEFAULT NULL,
  `asignacion_tie_of_reata` varchar(45) DEFAULT NULL,
  `asignacion_lìnea_de_vida` varchar(45) DEFAULT NULL,
  `asignacion_arrestador` varchar(45) DEFAULT NULL,
  `asignacion_casco_tipo_ii` varchar(45) DEFAULT NULL,
  `asignacion_arana_casco` varchar(45) DEFAULT NULL,
  `asignacion_barbuquejo` varchar(45) DEFAULT NULL,
  `asignacion_guantes_de_vaqueta` varchar(45) DEFAULT NULL,
  `asignacion_gafas` varchar(45) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preoperacional`
--

LOCK TABLES `preoperacional` WRITE;
/*!40000 ALTER TABLE `preoperacional` DISABLE KEYS */;
INSERT INTO `preoperacional` VALUES (4,'tencino','Bogota','nelson mora','s','moto','aaa111','2025','BAJAJ','123456798','2025-03-29','2025-03-28','2025-03-27','a','a','a','a','a','a','a',123456,'a','a','a','a','a','a','a','a','asd',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,7,'2025-03-02 20:54:44',NULL),(5,'tencino','Bogota','nelson mora','s','moto','aaa111','2025','BAJAJ','12345679','2025-03-12','2025-03-06','2025-03-12','1','1','1','1','1','1','1',123456,'0','0','0','0','0','0','0','0','qweq','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:04:34',NULL),(6,'tencino','Bogota','nelson mora','s','moto','aaa111','2025','BAJAJ','12345679','2025-03-12','2025-03-06','2025-03-12','1','1','1','1','1','1','1',123456,'0','0','0','0','0','0','0','0','qweq','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:08:48',NULL),(7,'tencino','Bogota','nelson mora','s','moto','aaa111','2025','BAJAJ','12345679','2025-03-02','2025-03-03','2025-03-04','1','1','0','0','0','0','0',12345,'0','0','0','0','0','0','0','0','adas','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:09:33',NULL),(8,'tencino','Bogota','nelson mora','s','moto','aaa111','2025','BAJAJ','12345679','2025-03-02','2025-03-03','2025-03-04','1','1','0','0','0','0','0',12345,'0','0','0','0','0','0','0','0','adas','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:11:13',NULL),(9,'tencino','Bogotá','NELSON DIAZ','s','moto','aaa111','2025','BAJAJ','12345679','2025-03-12','2025-03-09','2025-03-19','0','0','0','0','0','0','0',123456,'0','0','0','0','0','0','0','0','FDS','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:45:21',NULL),(10,'tencino','Bogotá','NELSON DIAZ','Sí','Moto','aaa111','2025','Yamaha','12345679','2025-03-15','2025-03-05','2025-03-18','0','0','0','0','0','0','0',123456,'0','0','0','0','0','0','0','0','SDF','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-02 23:55:27',NULL),(11,'tencino','Barranquilla','CARLOS CACERES','No','Camioneta','aaa111','2025','Kawasaki','12345679','2025-03-03','2025-03-03','2025-03-03','0','0','0','0','0','0','0',123456,'0','0','0','0','0','0','0','0','asd','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',7,'2025-03-03 19:09:20',NULL),(12,NULL,'Cartagena','SANDRA CORTES','Sí','Camión','aaa111','2025','Ford','B2','2025-03-03','2025-03-03','2025-03-03','regular','regular','regular','regular','regular','regular','0',12345,'regular','regular','regular','Sí','0','regular','regular','regular','sdfsdf','regular','regular','regular','regular','regular','regular','regular','regular','regular','regular','regular','0','0','0','0','0',7,'2025-03-03 20:26:24',NULL),(13,NULL,'Bogotá','DANIEL SILVA','No','Moto','aaa111','2025','Honda','A2','2025-03-03','2025-03-03','2025-03-03','regular','regular','regular','regular','regular','regular','regular',123456,'regular','regular','regular','Sí','0','regular','regular','regular','SDF','regular','regular','regular','regular','regular','regular','regular','regular','regular','regular','regular','0','0','0','0','0',23,'2025-03-03 22:20:23',NULL),(14,NULL,'Cali','MAURICIO MUÑOZ','Sí','Camioneta','bbb123','2025','Ducati','B2','2025-03-29','2025-03-29','2025-03-29','bueno','bueno','bueno','bueno','bueno','bueno','bueno',123456,'bueno','bueno','bueno','Sí','0','bueno','bueno','bueno','asdas','bueno','bueno','bueno','bueno','bueno','bueno','bueno','bueno','bueno','0','bueno','0','0','0','0','0',20,'2025-03-03 22:53:48',NULL),(15,NULL,'Medellín','SANDRA CORTES','Sí','Camión','bbb123','2025','Yamaha','C1','2025-03-03','2025-03-03','2025-03-03','malo','malo','malo','malo','malo','malo','malo',66666,'malo','malo','malo','Sí','0','malo','malo','malo','PREUEBA','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',74,'2025-03-03 23:01:21',NULL);
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
  `intentos_fallidos` int DEFAULT '0',
  `ultimo_intento` datetime DEFAULT NULL,
  PRIMARY KEY (`id_codigo_consumidor`),
  UNIQUE KEY `recurso_operativo_cedula` (`recurso_operativo_cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recurso_operativo`
--

LOCK TABLES `recurso_operativo` WRITE;
/*!40000 ALTER TABLE `recurso_operativo` DISABLE KEYS */;
INSERT INTO `recurso_operativo` VALUES (1,'80833959','$2b$12$aQ4qJp0DIfmO4Sn8bLLl6ePy2Gw0DvbILRiOhTot4mvTJNjx5nU1.',1,'Activo','VICTOR ALFONSO NARANJO SIERRA','DESARROLLADOR',0,NULL),(7,'1000954206','$2b$12$hsRuKP.8Zwfi5zKzyDgYz.6fPfM0M7T43r6jxrCx/8Y.7NAZ8IT/2',2,'Activo','DIANA SOSA','ANALISTA',0,NULL),(9,'123456789','$2b$12$lmSRIynNj8q3RBNF2am14eBOCua9QjVPAb5gbzifB4mYKzXhKzHpO',5,'Activo','FELIPE SANCHEZ','ANALISTA',0,NULL),(10,'test123','$2b$12$TbTyxYwNDGTrBnGfRT8r8uZ109IcbmcDfAmPMV80wTGkS4Pb2qBPa',1,'Activo','Usuario Test','Administrador',0,NULL),(11,'1019112308','$2b$12$aMNqQR8YmYwjLPV6N2SNKey0V/v95u0Yf47TPYQXTJZnbDEsCJReK',2,'Activo','ALARCON SALAS LUIS HERNANDO','TECNICO',0,NULL),(12,'80085017','$2b$12$MF9JAUqrMQEWcKo4/JB1Nubt.pk8YtYmkq6I1KqPMTkrRJcOMykC2',2,'Activo','ALDANA ALBA ALEXANDER','TECNICO',0,NULL),(13,'1085176966','$2b$12$/9wo6kghYrQ77FiSOZjTuePvMGtiFbVKY/A9fDhT3.J5jVpXBYncW',2,'Activo','ARNACHE ARIAS JUAN CARLOS','TECNICO',0,NULL),(14,'1023010816','$2b$12$Rt.Fs9yBz8JMYPc5A0cUk.NKh3PjXdhFQF6zhDGdTDOh6Liyhq98S',2,'Activo','AVILA BEJARANO YESSICA PAOLA','TECNICO',0,NULL),(15,'1022980482','$2b$12$x8.xhNxjy/8r5L.qSZA35eSh6wkzW88z2EuYtR77oQZ6puyh1kiqe',2,'Activo','AVILA RIVERA JESUS ALBERTO','TECNICO',0,NULL),(16,'1015449877','$2b$12$9Z33UtxocDoyas6TwYdZjODztyhdiGoVVcSerC44dFU9TDIe2HHvy',2,'Activo','BARRERA HERNANDEZ CAMILO EDUARDO','TECNICO',0,NULL),(17,'1022359872','$2b$12$VhRHVNsjSzDqF1Wn2Op/EOEInk5.NuKVJmZ8vPxSnTSvKfNyAVRIm',2,'Activo','BERNAL MORALES LUIS NELSON','TECNICO',0,NULL),(18,'1030545700','$2b$12$eGiXJ.veVQ6EJ3TWZ6SdYOcp2PRzyS1Wv4Sk8Ppo0zyryKcbTKIWK',2,'Activo','BETANCOURT CAAS DANIEL FRANCISCO','TECNICO',0,NULL),(19,'1032402333','$2b$12$BInLdQzVk6s.wff9yOXWLOy4Efuf21gWV.zygP3AGZsW2bnWyqjKW',2,'Activo','CACERES MARTINEZ CARLOS','TECNICO',0,NULL),(20,'1024484614','$2b$12$XuQK7WBvJFIfQu0KTGwpsuo6UjsTtvzcfcl7VrmcbxqNqFy4wvbgO',2,'Activo','CAMACHO CAMACHO HECTOR FABIAN','TECNICO',0,NULL),(21,'1019064898','$2b$12$XHoPSrrzykIiB6xuFXfcVOaIMTJRBRn7OwYTyATpq03hWyUjAnJz.',2,'Activo','CAMPOS VELANDIA ANDERSON FELIPE','TECNICO',0,NULL),(22,'1001090831','$2b$12$JpOGfWtVOehDbkEOlM61E.zO39FB9LOzELuurVCQ7D.0t3fVQSWG.',2,'Activo','CAIZALEZ RINCON JULIAN SANTIAGO','TECNICO',0,NULL),(23,'1049663304','$2b$12$vNNY/Ue8/qUxN9kB0tqNrO28E8farBhWgnk8cpzy0CJhsTCEz40tG',2,'Activo','CARRIZO MELGAREJO JORBER JOSE','TECNICO',0,NULL),(24,'79815202','$2b$12$Awi.YiYIQFibMo.LsMIi7OfZKI5JK1cVn89tAxbVXrVKNGCaa0Sj.',2,'Activo','CHAVEZ CRUZ NESTOR RAUL','TECNICO',0,NULL),(25,'1015455917','$2b$12$fZBJIYIZp8NYwOIgKYMT/.6EywCIaHhknLzcFnPjixNyxK1MD4yA.',2,'Activo','COLMENARES VARGAS YOHAN SEBASTIAN','TECNICO',0,NULL),(26,'52912112','$2b$12$X1u32vYpB9TokyjTLwcyMOMPWbBE4LdoUJTW33AfZCVYQs5G3TOva',2,'Activo','CORTES CUERVO SANDRA CECILIA','TECNICO',0,NULL),(27,'1045726635','$2b$12$.F/ibisFj.p0XVJ8AsTRweoIdqZrQKq30R17/LTQ4L9JEFiN9AMsK',2,'Activo','DIAZ BELEO GABRIELA ISABEL','TECNICO',0,NULL),(28,'1033758324','$2b$12$xfFSOLudsA6cEuBcZnpfae8hb.lrAbnsVMLXz9WJRNmXt6tEbjRGy',2,'Activo','DIAZ MORA FABIO NELSON','TECNICO',0,NULL),(29,'1193242759','$2b$12$ABrXaqGTMJ0W36FqHD.7EuPZCohtTLq8mn3bw8dFsopWNHSgji4Ry',2,'Activo','DUARTE EPIAYU EDER JOSE','TECNICO',0,NULL),(30,'1002407090','$2b$12$m84rFtqWR3SUprspLA2diemiDpfengNTBF1.Ls3AADLRhNUR68RmS',2,'Activo','ESPITIA BARON LICED JOANA','TECNICO',0,NULL),(31,'1073718147','$2b$12$iXjDy3x0hlQIyPj0Uxml.eZz55sn47mhq4VY/9FyU1AyAJuAobQTa',2,'Activo','FERIAS  CRUZ PAULA JOHANA','TECNICO',0,NULL),(32,'1024584584','$2b$12$/8F.h4ZO.7mU9dxyIow5wOKccTRmRv1454rE5ZVyXbrhiMym/wdkO',2,'Activo','GALAN CIPAGAUTA KAREN NATALIA','TECNICO',0,NULL),(33,'1070704868','$2b$12$ojrx9FUBU9g3b0M9j8L0LOMLzzM7wB2n/c643S5ECO41rvKO3nYJS',2,'Activo','GOMEZ BERNAL JOSE TOMAS','TECNICO',0,NULL),(34,'1072073893','$2b$12$1jcFx02eTQ.EWzx283Cz6uL3.zDS2aKgqLAcA1VQEsr3x13JXIcP2',2,'Activo','GUTIERREZ SOLANO BRAYAN FERNANDO','TECNICO',0,NULL),(35,'1070964489','$2b$12$XMNLnLuVM9rhxX.DSqGb/.yDWFj6OYR0ftwFDGSLZpKFvnInfzggu',2,'Activo','HERRERA PINZON JAVIER ORLANDO','TECNICO',0,NULL),(36,'1002455544','$2b$12$5TeLGxOK5ZjSfVwH8SpYGe95pmNgCcYHhrLVtT/Q6W2rGlL5ttY.K',2,'Activo','LANCHEROS ALARCON CESAR ARNULFO','TECNICO',0,NULL),(37,'1019121754','$2b$12$qs85UnQ8LxGU36UOhizmROBBH6Q.ZUdVSY85nNsrjtHA14oGocXnS',2,'Activo','LANCHEROS ALARCON JOSE EDILFONSO','TECNICO',0,NULL),(38,'1033779919','$2b$12$Ear7cHFiUqN50o1e3RJXv.PyE3/TmAJC2Ms.YTh3f63Yg6Wqvcr.e',2,'Activo','LANCHEROS GONZALEZ EDITON DAVID','TECNICO',0,NULL),(39,'1032506059','$2b$12$5SzdRmYUN953dg2zZFYfjuZ0C0h1DwINjLWqGntbpcQNm/z1NdTMq',2,'Activo','LOPEZ SALAMANCA BRIAM SNEIDER','TECNICO',0,NULL),(40,'1102119224','$2b$12$dcuf03b.bG/rKs9cfF8Ey.M4xoLEUYHK08gFyLS/2ajzbcPRc/CWO',2,'Activo','MACEA MARTELO LUIS ALBERTO','TECNICO',0,NULL),(41,'80543481','$2b$12$5M06xa6hCyl3o3wZBzynouSoOv1lSXI78cQYQIP8B6dAGLN7GtMKy',2,'Activo','MALDONADO GARNICA JAVIER HERNANDO','TECNICO',0,NULL),(42,'1016092318','$2b$12$JrYsMRmnrTBXKG01xPzr1u5s6qftR435H0cHIqNKMInaNxpsFguaG',2,'Activo','MARIN HERNANDEZ MIGUEL ANGEL','TECNICO',0,NULL),(43,'1023026702','$2b$12$4SnLNJVqdVv.A/o/ETFq5.jnnGhnJmHIm.nZpsCM79R3eayuH16t.',2,'Activo','MARIN REINA JEFERSON CAMILO','TECNICO',0,NULL),(44,'1014216655','$2b$12$TlqNAiQNY/GfZBQDuVmScOsJNbVbeF92afALcySylFVakl1/QEjQa',2,'Activo','MARTIN MARTINEZ JULIAN CAMILO','TECNICO',0,NULL),(45,'1004283704','$2b$12$jMBY0pv6wOknEoUO9JAEuOfJtrOjuDqqdqJ90jh55m0MiFkkpFSE.',2,'Activo','MENDOZA FLOREZ DIEGO DE JESUS','TECNICO',0,NULL),(46,'12634949','$2b$12$jNdz.yDLQo2IZGPFK4ZEVuPkOivhpdKcsc0Wg/WwZGkV/Fl2J0kCG',2,'Activo','MONSALVO LOPEZ LAINER JAIR','TECNICO',0,NULL),(47,'19591545','$2b$12$xTGFLR3MwiH4oCLjYlq0TeiQX0fjBy4rzJoHrg29FGBPpTLb29kSW',2,'Activo','MONTENEGRO MEZA ALDON REMBER','TECNICO',0,NULL),(48,'1007651234','$2b$12$aaxHI.ak9R20ZlTNUu6Y8uC6v2R6hajijU7fK6A1jMAnUaGiJNQai',2,'Activo','MORA PEREZ EDUARD CAMILO','TECNICO',0,NULL),(49,'1014212844','$2b$12$nun.TEw7hxFFEg3F99ip.e.6ZcgakpVZNKdHUNadhXle6VXTufJei',2,'Activo','MORENO MENDOZA EDWIN MAURICIO','TECNICO',0,NULL),(50,'80091070','$2b$12$BoK.kwxWngMK6FsEOJ/1XOLLz1SBTgj2du0mPZmGjYYpnEObPZnca',2,'Activo','MUOZ URREGO JOSE MAURICIO','TECNICO',0,NULL),(51,'1012411088','$2b$12$7JMQzic1a/nhFGtEGZRLyO.Qv5ZAWQtlOgkEoASactBw2VmB6y2b2',2,'Activo','NARANJO TAVERA ANDERSON JULIAN','TECNICO',0,NULL),(52,'79827363','$2b$12$iLbH8XUqppKvVlHIuIIs4O/vk6jAb9jDaxpsFaCb7CUM4M9RGVpWi',2,'Activo','NOVOA  RINCON JOSE VICENTE ','TECNICO',0,NULL),(53,'1143833247','$2b$12$Ac5Ai661yJEQwek4khwNceQL1RkrhkRoQPj.KNEjEXIWhLJ0G53KO',2,'Activo','OCAMPO GONZALEZ JULIAN','TECNICO',0,NULL),(54,'84455827','$2b$12$DL8aoVwzFOGMGpo6JhJjW.7JK7uPJm7mY/yj9DEIGsKGh4l6bi7yi',2,'Activo','OATE MERCADO ERNESTO RAFAEL','TECNICO',0,NULL),(55,'1026292931','$2b$12$bPp15Ga7/qoIrKbcjdGv/OlaNXzsk5IgwY5oCyL8WoiCUYrjqq/nu',2,'Activo','ORTIZ GARZON SERGIO YOHAN','TECNICO',0,NULL),(56,'1020774885','$2b$12$uCsx1nRi2FsnsaLnrckWnegF5qRi33c7gbGPG/bh1vGdjOtU9sIja',2,'Activo','ORTIZ SUAREZ JESSY ESTEBAN','TECNICO',0,NULL),(57,'1065807926','$2b$12$ab8K.OSSPc/qtQ9Vg9Mw0OjHB5aI7DLJqI6NXavBPN7WQTTpYpR3i',2,'Activo','PADILLA MERCADO OMAR YESITH','TECNICO',0,NULL),(58,'1020809768','$2b$12$lqoAUHLbU5XnLjqt9LtDA.sLGoKD7b0F1rJ5xU4ZWKzcQEmenPqfm',2,'Activo','PADILLA MORALES LUIS ALFONSO','TECNICO',0,NULL),(59,'1007611824','$2b$12$ePWFPQWR6OckqtxB8MhideyiEnrqmMPo2Yj1Hwr/X0duPXFed/JXi',2,'Activo','PATERNINA SIERRA GUSTAVO ELIAS','TECNICO',0,NULL),(60,'1067725686','$2b$12$7M8YY8PtJl2SpZ37CqafwenNzT.Naoq5hA/UdmxZxxV1xtqO6sxRi',2,'Activo','PEDRAZA CABALLERO JORDYN JAIR','TECNICO',0,NULL),(61,'79797613','$2b$12$EHzPn4kmz5HFikZdk5CX5OT1GPL5vZjGvU6UEakSlGyfi27gNpMq2',2,'Activo','PINEDA NARANJO HERMAN','TECNICO',0,NULL),(62,'1105786374','$2b$12$tz1v2LGZF2x2iJTcGSAOIeaP4qP0rWaqLdZUC4e6nqS3YZNWF54sy',2,'Activo','PULIDO VEGA CRISTHIAN FERNANDO','TECNICO',0,NULL),(63,'1065840853','$2b$12$WoF9us.8TX2HLNf.7CJ0Ve2x8uwuwuIXOnz2W8ZrLdInq98NIvqxi',2,'Activo','QUINTERO OATE SILFREDO SEGUNDO','TECNICO',0,NULL),(64,'1003479597','$2b$12$8zZGIrdzc5YUluH3oRaZ6uvMeu8fEXCv1bUZsW0EeJ11.521kMcem',2,'Activo','RAMOS BARACALDO JUAN CARLOS','TECNICO',0,NULL),(65,'1033692973','$2b$12$DOTu0V3UtNo4D9viIvZtBudSBE1kQnBKvVrPtW1F23vWs/obTQyj2',2,'Activo','REYES CAMARGO JOSE ALEJANDRO','TECNICO',0,NULL),(66,'1015438296','$2b$12$XtQrmOgeUaMxwXZmF8Rmnuq6T9/vbQeCSKRdctGk/HCSDFfbWHWdO',2,'Activo','REYES TOBASURA CRISTIAN ESTIVEN','TECNICO',0,NULL),(67,'1007701149','$2b$12$phHdvrxGvAedTnguiYo8demFEaVzSE5kfQhTy0Egwof0x4ryn1Y92',2,'Activo','RODRIGUEZ RODRIGUEZ JUAN JOSE','TECNICO',0,NULL),(68,'1015408904','$2b$12$oto/0vvdAyIwsxJncAscC.c3BVqD61zDdVp6FmwzeTubmfqVB8EHG',2,'Activo','RODRIGUEZ SERGIO SAMUEL','TECNICO',0,NULL),(69,'1032474386','$2b$12$BwnNeVjI3Tsm.7ZGWEO9dOS/4JdKsondUfLwo9bFx3C7FaqE3ILVW',2,'Activo','ROMERO MARTINEZ BRAYAN ARILSON','TECNICO',0,NULL),(70,'1052339761','$2b$12$fW0vzmIQGrvjO9cmELCdy.FXpzhma5A9V9mAIjb.I.R50EICZiox6',2,'Activo','SANCHEZ PEA CARLOS HERNANDO','TECNICO',0,NULL),(71,'1019093439','$2b$12$/8z250RbuYH5KxNsJj/vme2.bCrGERe.Dz9uZsZskFxF/TTS.hJYa',2,'Activo','SANCHEZ PEA JUAN GABRIEL','TECNICO',0,NULL),(72,'1033764826','$2b$12$qXjv8gIoprJeHOGRlaE5Gu4Hl2XEOzCehEmvI8RYKU4nRZd2rOshq',2,'Activo','SIERRA HERNANDEZ ROBINSON ALEXANDER','TECNICO',0,NULL),(73,'1016073769','$2b$12$XpQuddp8VpB145hcUmidNuQWWdHYfAzFmpjjJ5cBEpz9R2CHomi76',2,'Activo','SILVA CASTRO DANIEL ALBERTO','TECNICO',0,NULL),(74,'1002407101','$2b$12$XFPthxh2Kx69MF9GiU4GXOscrcm4s0qb5Ai6P/Hdi4rJfhImfAoX.',2,'Activo','SOSA GARCIA DIANA CAROLINA','TECNICO',0,NULL),(75,'1051287107','$2b$12$ZJCdeJ6yl1Ta0dcy/HSDcufrZJ40fZgwdOTZg9uXlH7UfUjC5eNrS',2,'Activo','SOSA GARCIA JORGE ARMANDO','TECNICO',0,NULL),(76,'1233904351','$2b$12$Xg4LXEJJLQ0NI2qSZhskfe86azp3mGk8CU9BPd8KdDLaAWFY60XIO',2,'Activo','SUESCA NEIRA MAURICIO ESTEBAN','TECNICO',0,NULL),(77,'1020781801','$2b$12$bb0Pqpy9nf4j1H0cXSRs4eVRSdX1nJVWvOmdy4gVtkOW8CLvxYgKi',2,'Activo','TIGUAQUE DIAZ RONNY ALEJANDRO','TECNICO',0,NULL),(78,'1116205069','$2b$12$PkkPjeboKtnYaxLcBABMxeqUgruIlEBR/D3UJY6pqa1h/K2Vn48bS',2,'Activo','TIQUE LOAIZA JOHN JAIRO','TECNICO',0,NULL),(79,'1007158261','$2b$12$/cACG6nFFJ21UH39sS/9S.0M89HB0S10.NsGdU6GaIROjf4lVQSbu',2,'Activo','TORRES RINCON MIGUEL ANGEL','TECNICO',0,NULL),(80,'79763158','$2b$12$OYvibdqQoAHbTxTtmFJ8TenGY.zonNM3xMInf6kY7U1vyVlWR84Oy',2,'Activo','TRUJILLO RAMIREZ LUIS ALBERTO','TECNICO',0,NULL),(81,'1019069738','$2b$12$nWEIBCdgV1wEDREa6WqFDu8BH.kPJRe782YxgEq8M49CzphiWcx0S',2,'Activo','URREA CALVO LEIDY SOLANYI','TECNICO',0,NULL),(82,'1007770364','$2b$12$b9vra0ta3.BARz6HRMc.yOYFOipl7jrbq2lZrv0jDq7ONFkO00uLu',2,'Activo','VALIENTE PINZON EDISSON CAMILO','TECNICO',0,NULL),(83,'23533027','$2b$12$gCzqRagkXjEiJT0g5Zo32uhpAM/cMauuK9V8mqCE6QIpnc.Sygin2',2,'Activo','VELANDIA GARCIA LUZ DARY','TECNICO',0,NULL),(84,'80034211','$2b$12$X84kJ4iQR33bVPKCUEaRN.D.gGgX5VnU3AJgdk4nzC8Wd6zDmAn3y',2,'Activo','VELANDIA REDONDO DIEGO ALEXANDER','TECNICO',0,NULL),(85,'76009268','$2b$12$.TDXFuBwfrP4lmvM9V9T4.fcTKapwj4JCsIwQV7AnjeZ7NM53VHB.',2,'Activo','VELASCO FERNANDEZ JESUS LEONIDAS','TECNICO',0,NULL),(86,'1110180337','$2b$12$qnP.slwoyqYYjUYh1HxJwejOPePJLzr/EmYGrYPMb7Y9laGX0oGVC',2,'Activo','VERGARA TRUQUE SERGIO','TECNICO',0,NULL),(87,'1085229001','$2b$12$sUhMTckjVqrHJ5lf6PSlYeRpq6kJ2B7pdURdSdxILBLFCXZdEsVva',2,'Activo','YEPES CARO DEINER JOSE','TECNICO',0,NULL),(88,'24198720','$2b$12$o0wvN3vXoxu82bWtNCoZXuUUD6UssBKgMDzd0Q.Y7e4JPtMac4iie',2,'Activo',' ALONSO OTALORA BLANCA IRENE ','TECNICO',0,NULL),(89,'1233489456','$2b$12$iC.esOaEucJhZ.q3A96kIuddvCVciI.HpFSS9Tf66vIOcW5n/U5PW',2,'Activo','SILVA RIVERA JESSICA LORENA','TECNICO',0,NULL),(90,'1123530243','$2b$12$EOXyo2/OnE45dKDRTJT9OeOAaUvZTsjf1ZmMwXQ7EGbY9JlMvMQjK',2,'Activo','BEJARANO QUEZADA EDWIN','TECNICO',0,NULL),(91,'1014188955','$2b$12$8sdBGtCDgAvKAvcCl4UqlOKAm2KXJ67OZO3cNdwRE/Vbq.AElM0bC',2,'Activo','LOZANO CASTAEDA JOHAN DAVID','TECNICO',0,NULL),(92,'1012372297','$2b$12$CkisLIeXBYEhM/4yEn8vmeD2JSSex8Zm16lzYlrwZvvsZFvtZk8Wm',2,'Activo','MORA LOPEZ JUAN CARLOS ','TECNICO',0,NULL),(93,'79832366','$2b$12$M1OuQoSHja/8kspHwf.lbONz6wTDNfl9pP.ZfFO8Ikb2myVL.qN8K',2,'Activo','MIRANDA RAMIREZ LUIS CARLOS','TECNICO',0,NULL),(94,'5694500','$2b$12$Nl.ttmXBBq0pPzJ5wI2LRea3S2dHFOxzjH/Lu9bfM66eZrald9ZBq',2,'Activo','SILVA LANDAEZ MAIKEL SILVERIO','TECNICO',0,NULL),(95,'1085174519','$2b$12$27USuKj52jReVgVRH5VmxOpbhvrINIOUopImpBfsLwrlWxRDgnmmy',2,'Activo','JHON MARIO LASCARRO DIAZ','TECNICO',0,NULL),(96,'5043240','$2b$12$Nqf1Q2t9gVOPsug9USV5aesid2eW5LnLJTF04/IC2UmeQc9dCUQeO',2,'Activo','RAFAEL JOSE COLINA ESCALONA','TECNICO',0,NULL),(97,'80895801','$2b$12$g9.qT3UjnVq3nqDTvmMRfuOioULiB4cI5p8H1dvIjSjl75WDLtOvG',2,'Activo','ANDRES FELIPE AYA MORENO','TECNICO',0,NULL);
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

-- Dump completed on 2025-03-03 23:17:07
