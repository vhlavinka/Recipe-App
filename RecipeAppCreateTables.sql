DROP TABLE Users;
DROP TABLE User_Lists;
DROP TABLE Recipes;
DROP TABLE List_Items;
DROP TABLE Items;


CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS User_Lists (
  list_id INT AUTO_INCREMENT NOT NULL,
  user_id INT NOT NULL,
  list_title VARCHAR(100) NOT NULL,
  PRIMARY KEY(list_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS Recipes (
  recipe_id INT AUTO_INCREMENT NOT NULL,
  description VARCHAR(100) NOT NULL,
  instructions VARCHAR(5000),
  PRIMARY KEY (recipe_id)
);

CREATE TABLE IF NOT EXISTS Items (
  item_id INT AUTO_INCREMENT NOT NULL,
  description VARCHAR(100) NOT NULL,
  PRIMARY KEY (item_id)
);

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

CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
  unit_id INT AUTO_INCREMENT NOT NULL,
  recipe_id INT NOT NULL,
  item_id INT NOT NULL,
  measurements VARCHAR(100),
  PRIMARY KEY (unit_id),
  FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id),
  FOREIGN KEY (item_id) REFERENCES Items (item_id)
);
