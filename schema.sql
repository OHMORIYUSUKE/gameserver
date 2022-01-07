DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `room_info`;
DROP TABLE IF EXISTS `user_in_room`;
DROP TABLE IF EXISTS `user_result`;

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
  `room_id` bigint NOT NULL,
  `user_id` int DEFAULT 1,
  `name` varchar(255) DEFAULT NULL,
  `leader_card_id` int DEFAULT NULL,
  `select_difficulty` int DEFAULT NULL,
  `is_me` boolean DEFAULT NULL,
  `is_host` boolean DEFAULT NULL,
  PRIMARY KEY (`room_id`,`user_id`)
);

CREATE TABLE `user_result` (
  `room_id` bigint NOT NULL,
  `user_id` int DEFAULT 1,
  `judge_count_list` varchar(255) DEFAULT NULL,
  `score` int DEFAULT NULL,
  PRIMARY KEY (`room_id`,`user_id`)
);
