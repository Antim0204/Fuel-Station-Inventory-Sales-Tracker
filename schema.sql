CREATE TABLE fuel_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(80) UNIQUE NOT NULL,
  price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE inventory (
  id SERIAL PRIMARY KEY,
  fuel_type_id INT NOT NULL UNIQUE REFERENCES fuel_types(id) ON DELETE CASCADE,
  litres NUMERIC(12,3) NOT NULL CHECK (litres >= 0) DEFAULT 0
);

CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  fuel_type_id INT REFERENCES fuel_types(id) ON DELETE SET NULL,
  litres NUMERIC(12,3) NOT NULL CHECK (litres > 0),
  price_at_sale NUMERIC(10,2) NOT NULL CHECK (price_at_sale >= 0),
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
