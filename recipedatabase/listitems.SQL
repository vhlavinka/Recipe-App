CREATE TABLE IF NOT EXISTS List_Items (
  unit_id INT AUTO_INCREMENT NOT NULL,
  list_id INT NOT NULL,
  item_id INT NOT NULL,
  recipe_id INT,
  checked INT DEFAULT 0,
  PRIMARY KEY (unit_id),
  FOREIGN KEY (list_id) REFERENCES User_Lists (list_id),
  FOREIGN KEY (item_id) REFERENCES Items (item_id),
  FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id)
);
