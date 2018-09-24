CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
  unit_id INT AUTO_INCREMENT NOT NULL,
  recipe_id INT NOT NULL,
  item_id INT NOT NULL,
  measurements VARCHAR(100),
  PRIMARY KEY (unit_id),
  FOREIGN KEY (recipe_id) REFERENCES Recipe (recipe_id)
);
