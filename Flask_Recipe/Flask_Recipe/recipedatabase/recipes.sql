CREATE TABLE IF NOT EXISTS recipes (
  recipe_id INT AUTO_INCREMENT NOT NULL,
  description VARCHAR(100) NOT NULL,
  instructions VARCHAR(5000),
  PRIMARY KEY (recipe_id)
);
