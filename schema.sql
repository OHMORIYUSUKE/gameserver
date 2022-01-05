DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `room_info`;

CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `leader_card_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`)
);

CREATE TABLE `room_info` (
  `room_id` bigint NOT NULL AUTO_INCREMENT,
  `live_id` int DEFAULT NULL,
  `joined_user_count` int DEFAULT 1,
  `max_user_count` int DEFAULT NULL,
  `is_active` boolean DEFAULT true,
  PRIMARY KEY (`room_id`)
);

CREATE TABLE `user_in_room` (
  `room_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `leader_card_id` int DEFAULT NULL,
  `select_difficulty` int DEFAULT NULL,
  `is_me` boolean DEFAULT NULL,
  `is_host` boolean DEFAULT NULL,
  PRIMARY KEY (`room_id`)
  CONSTRAINT `fk_room_id`
    FOREIGN KEY (`room_id`) 
    REFERENCES `room_info` (`room_id`)
);

INSERT INTO user(id,name,token,leader_card_id) VALUES (0,'ほのか','asdfghjkl','12345');
INSERT INTO user(id,name,token,leader_card_id) VALUES (0,'ことり','zxcv','88998');
INSERT INTO user(id,name,token,leader_card_id) VALUES (0,'うみ','qwert','173248');

INSERT INTO user
  (id,name,token,leader_card_id)
VALUES 
  (0,'ほのか','asdfghjkl','12345'),
  (0,'ことり','zxcv','88998'),
  (0,'うみ','qwert','173248');

SELECT * FROM user WHERE name='うみ';

SELECT * FROM user WHERE name LIKE 'ほ%';
