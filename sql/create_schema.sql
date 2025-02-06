CREATE DATABASE flashcard_db CHARACTER SET utf8 COLLATE utf8_bin;
CREATE USER 'flashcarduser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Group1!';
GRANT ALL PRIVILEGES ON flashcard_db.* TO 'flashcarduser'@'localhost';
FLUSH PRIVILEGES;

USE flashcard_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE flashcard_sets (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    is_shared TINYINT(1) DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, 
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE flashcards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    set_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    is_active TINYINT(1) DEFAULT 1, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (set_id) REFERENCES flashcard_sets(set_id) ON DELETE CASCADE
);

CREATE TABLE progress_tracking (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    card_id INT NOT NULL,
    correctly_answered INT DEFAULT 0,
    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES flashcards(card_id) ON DELETE CASCADE
);