CREATE DATABASE reservas;

USE reservas;

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    senha VARCHAR(255)
);

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT,
    tipo VARCHAR(255),
    capacidade INT,
    descricao TEXT
);

CREATE TABLE reservas (
    id_reserva VARCHAR(10) PRIMARY KEY,
    sala_id INT,
    inicio DATETIME,
    fim DATETIME,
    usuario VARCHAR(255),
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE
);

SELECT * 
FROM usuario;

SELECT * 
FROM salas;

SELECT * 
FROM reservas;