CREATE TABLE `perm_permission` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `title` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
      `code` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_permission_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `perm_super_admin` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `email` varchar(128) NOT NULL,
      `password` varchar(128) NOT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_super_admin_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `perm_user_group` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `title` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
      `code` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_user_group_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `perm_user_group_member` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `user_id` int(11) NOT NULL,
      `user_group_id` int(11) NOT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_user_in_user_group` (`user_id`,`user_group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `perm_user_group_permission` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `user_group_id` int(11) NOT NULL,
      `permission_id` int(11) NOT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_user_permission` (`user_group_id`,`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `perm_user_permission` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `user_id` int(11) NOT NULL,
      `permission_id` int(11) NOT NULL,
      `created_at` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_user_permission` (`user_id`,`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
