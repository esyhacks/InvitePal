CREATE DATABASE Referral_Data;

USE Referral_Data;

-- Users Table
CREATE TABLE Users (
    telegram_id BIGINT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    referred_by BIGINT DEFAULT NULL, 
    points_available INT DEFAULT 0,
    is_joined BOOLEAN NOT NULL,
    points_credited BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (referred_by) REFERENCES Users(telegram_id) ON DELETE SET NULL -- Referencing the same table for the referral
);

-- Rewards Table
CREATE TABLE Rewards (
    item_id INT PRIMARY KEY,
    item_description VARCHAR(255) NOT NULL,
    points_required INT NOT NULL,
    secret_1 VARCHAR(255) NOT NULL,
    secret_2 VARCHAR(255)NOT NULL,
    redeemed_count INT DEFAULT 0,
    max_count INT DEFAULT 0
);

-- Data insertion for rewards
INSERT INTO Rewards (item_id, item_description, points_required, secret_1, secret_2, redeemed_count, max_count) 
VALUES
(401, 'E-Book Reader Subscription - 1 Year', 200, 'user001@library.com', 'Key!Read2023', 0, 10),
(402, 'Music Streaming Service - 6 Month Plan', 150, 'user002@musicstream.com', 'Tune#Safe789', 1, 8),
(403, 'Online Fitness Plan - 3 Months', 100, 'user003@fitmail.com', 'Workout@123', 2, 7),
(404, 'Coding Bootcamp Voucher', 250, 'user004@eduportal.com', 'Code@Master', 0, 5),
(405, 'Photo Editing Software - Annual License', 300, 'user005@photoapp.com', 'EditPro@2024', 0, 3),
(406, 'VPN Service - Lifetime Access', 400, 'user006@securevpn.com', 'SecureVPN#1', 1, 2),
(407, 'Language Learning Subscription - 1 Year', 180, 'user007@langlearn.com', 'LangPro2023!', 0, 6),
(408, 'Secure Storage - 2 Year Plan', 350, 'user008@cloudservice.com', 'Storage#Safe', 0, 3),
(409, 'Gaming Service Pass - 1 Year', 500, 'user009@gamepass.com', 'GameOn@500', 0, 2),
(410, 'Digital Magazine - 6 Month Access', 120, 'user010@magazine.com', 'Mag6Months@Key', 0, 7);

-- Data insertion for users
INSERT INTO users (telegram_id, username, referred_by, points_available, is_joined, points_credited) 
VALUES 
(876543210, 'UserOmega', NULL, 1200, 1, 1),
(987654321, 'UserSigma', 876543210, 800, 1, 0),
(123456789, 'UserAlpha', NULL, 1500, 1, 1),
(234567890, 'UserBeta', 123456789, 600, 1, 0),
(345678901, 'UserGamma', 987654321, 900, 1, 1);




