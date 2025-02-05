CREATE DATABASE flashcard_db CHARACTER SET utf8 COLLATE utf8_bin;
CREATE USER 'flashcarduser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Group1!';
GRANT ALL PRIVILEGES ON flashcard_db.* TO 'flashcarduser'@'localhost';
FLUSH PRIVILEGES;