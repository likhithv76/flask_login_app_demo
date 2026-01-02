CREATE DATABASE flask_login;
USE flask_login;
CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(100) UNIQUE,
 password VARCHAR(255)
);
INSERT INTO users(username,password) VALUES('admin','admin123');