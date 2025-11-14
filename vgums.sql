
drop database vgums_db;
CREATE DATABASE IF NOT EXISTS vgums_db;
USE vgums_db;

CREATE TABLE IF NOT EXISTS Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255) DEFAULT 'default_avatar.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS User_Roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    genre VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Player_Progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    score INT DEFAULT 0,
    level_achieved INT DEFAULT 1,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id, game_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
);


INSERT IGNORE INTO Roles (role_name) VALUES ('Player'), ('Admin');

INSERT IGNORE INTO Users (username, email, password_hash) VALUES
('admin', 'admin@vgums.com', 'admin'),
('PlayerOne', 'p1@vgums.com', 'p1pass'),
('PlayerTwo', 'p2@vgums.com', 'p2pass'),
('ProGamer23', 'pro@vgums.com', 'propass');

INSERT IGNORE INTO User_Roles (user_id, role_id) VALUES
(1, 2), -- admin is Admin
(2, 1), (3, 1), (4, 1);

INSERT IGNORE INTO Games (title, description, genre) VALUES
('Cosmic Rift', 'Sci-Fi space shooter', 'Shooter'),
('Mystic Forest', 'Fantasy RPG adventure', 'RPG'),
('Speed-Run City', 'High-speed urban racer', 'Racing');

INSERT IGNORE INTO Player_Progress (user_id, game_id, score, level_achieved) VALUES
(2, 1, 15000, 12),
(2, 2, 500, 3),
(3, 1, 25000, 18),
(4, 1, 175000, 99),
(4, 3, 5000, 5);



DELIMITER //

CREATE PROCEDURE sp_RegisterUser(
    IN p_username VARCHAR(100),
    IN p_email VARCHAR(255),
    IN p_password_hash VARCHAR(255)
)
BEGIN
    INSERT INTO Users (username, email, password_hash)
    VALUES (p_username, p_email, p_password_hash);
END//

CREATE PROCEDURE sp_AuthenticateUser(
    IN p_username VARCHAR(100),
    IN p_password_hash VARCHAR(255)
)
BEGIN
    SELECT user_id, username, email, avatar_url
    FROM Users
    WHERE username = p_username AND password_hash = p_password_hash;
END//

CREATE PROCEDURE sp_AdminAddGame(
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_genre VARCHAR(100)
)
BEGIN
    INSERT INTO Games (title, description, genre)
    VALUES (p_title, p_description, p_genre);
END//

CREATE PROCEDURE sp_UpdatePlayerScore(
    IN p_user_id INT,
    IN p_game_id INT,
    IN p_new_score INT
)
BEGIN
    DECLARE new_level INT;
    SET new_level = 1 + (p_new_score DIV 5000);

    INSERT INTO Player_Progress (user_id, game_id, score, level_achieved)
    VALUES (p_user_id, p_game_id, p_new_score, new_level)
    ON DUPLICATE KEY UPDATE
        score = VALUES(score),
        level_achieved = VALUES(level_achieved),
        last_played = CURRENT_TIMESTAMP;
END//

DELIMITER ;


DELIMITER //

CREATE TRIGGER trg_AfterUserInsert
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    INSERT INTO User_Roles (user_id, role_id) VALUES (NEW.user_id, 1);
END//

DELIMITER ;


CREATE OR REPLACE VIEW v_Leaderboard_CosmicRift AS
SELECT
    u.username,
    p.score,
    p.level_achieved,
    p.last_played
FROM Player_Progress p
JOIN Users u ON p.user_id = u.user_id
WHERE p.game_id = 1
ORDER BY p.score DESC
LIMIT 100;

CREATE OR REPLACE VIEW v_Admin_UserReport AS
SELECT
    u.user_id,
    u.username,
    u.email,
    u.created_at,
    r.role_name
FROM Users u
JOIN User_Roles ur ON u.user_id = ur.user_id
JOIN Roles r ON ur.role_id = r.role_id;

DELIMITER //

CREATE FUNCTION fn_GetUserEmail(p_user_id INT)
RETURNS VARCHAR(255)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE result_email VARCHAR(255);
    SELECT email INTO result_email FROM Users WHERE user_id = p_user_id;
    RETURN result_email;
END//

DELIMITER ;

DELIMITER //

CREATE PROCEDURE sp_DeleteGame(
    IN p_game_id INT
)
BEGIN
    DELETE FROM Games WHERE game_id = p_game_id;
END//

DELIMITER ;


GRANT ALL PRIVILEGES ON vgums_db.* TO 'admin'@'%';

GRANT EXECUTE ON PROCEDURE vgums_db.sp_AdminAddGame TO 'admin'@'%';
GRANT EXECUTE ON PROCEDURE vgums_db.sp_DeleteGame TO 'admin'@'%';

REVOKE INSERT, UPDATE, DELETE ON vgums_db.Games FROM 'player_user'@'%';
REVOKE EXECUTE ON PROCEDURE vgums_db.sp_AdminAddGame FROM 'player_user'@'%';


SELECT username, score
FROM Users u
JOIN Player_Progress p ON u.user_id = p.user_id
WHERE p.game_id = 1
  AND p.score > (
        SELECT AVG(score)
        FROM Player_Progress
        WHERE game_id = 1
  );

SELECT g.title, COUNT(p.user_id) AS total_players
FROM Games g
LEFT JOIN Player_Progress p ON g.game_id = p.game_id
GROUP BY g.game_id, g.title;

DELIMITER //

CREATE TRIGGER trg_UpdateLastPlayed
BEFORE UPDATE ON Player_Progress
FOR EACH ROW
BEGIN
    IF NEW.score <> OLD.score OR NEW.level_achieved <> OLD.level_achieved THEN
        SET NEW.last_played = CURRENT_TIMESTAMP;
    END IF;
END//

DELIMITER ;



