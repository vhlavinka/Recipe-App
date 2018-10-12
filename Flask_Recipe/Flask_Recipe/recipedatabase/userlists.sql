CREATE TABLE IF NOT EXISTS User_Lists (
  list_id INT AUTO_INCREMENT NOT NULL,
  user_id INT NOT NULL,
  list_title VARCHAR(100) NOT NULL,
  PRIMARY KEY(list_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);
