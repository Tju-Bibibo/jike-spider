/*
Navicat MySQL Data Transfer

Source Server         : 主机
Source Server Version : 50714
Source Host           : localhost:3306
Source Database       : jike

Target Server Type    : MYSQL
Target Server Version : 50714
File Encoding         : 65001

Date: 2018-11-13 23:45:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `jike_user`
-- ----------------------------
DROP TABLE IF EXISTS `jike_user`;
CREATE TABLE `jike_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `screenName` text CHARACTER SET utf8mb4,
  `createdAt` text CHARACTER SET utf8mb4,
  `updatedAt` text CHARACTER SET utf8mb4,
  `isVerified` text CHARACTER SET utf8mb4,
  `verifyMessage` text,
  `briefIntro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `bio` text CHARACTER SET utf8mb4,
  `thumbnailUrl` text CHARACTER SET utf8mb4,
  `picUrl` text,
  `gender` text,
  `city` text,
  `country` text,
  `province` text,
  `following` text,
  `ref` text,
  `topicSubscribed` text,
  `topicCreated` text,
  `followedCount` text,
  `followingCount` text,
  `highlightedPersonalUpdates` text,
  `liked` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of jike_user
-- ----------------------------
