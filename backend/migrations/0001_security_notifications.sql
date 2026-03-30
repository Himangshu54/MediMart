-- Add refresh token storage
CREATE TABLE IF NOT EXISTS REFRESH_TOKEN (
  token_id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  role VARCHAR(50) NOT NULL,
  token_hash VARCHAR(64) NOT NULL,
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (token_id),
  UNIQUE KEY uniq_refresh_token_hash (token_hash),
  KEY idx_refresh_token_user (user_id, role)
);

-- Extend order status enum values
ALTER TABLE ORDERS
  MODIFY order_status ENUM('PENDING','ACCEPTED','REJECTED','SHIPPED','DELIVERED','CANCELLED')
  NOT NULL DEFAULT 'PENDING';
