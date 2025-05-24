CREATE DATABASE latidoapp2;

USE latidoapp2;

CREATE TABLE mediciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100),
    fecha DATETIME,
    audio_nombre VARCHAR(255)
);