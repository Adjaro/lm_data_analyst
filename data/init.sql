CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    date DATE,
    product VARCHAR(100),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    customer_age INTEGER
);

-- Insertion de données d'exemple
INSERT INTO sales (date, product, category, amount, customer_age) VALUES
('2023-01-01', 'Laptop Pro', 'Électronique', 999.99, 35),
('2023-01-02', 'Smartphone X', 'Électronique', 699.99, 28),
('2023-01-03', 'Tablette Y', 'Électronique', 499.99, 42),
('2023-01-04', 'T-shirt Basic', 'Vêtements', 29.99, 25),
('2023-01-05', 'Jean Classic', 'Vêtements', 79.99, 31),
('2023-01-06', 'Chaussures Sport', 'Vêtements', 89.99, 27),
('2023-01-07', 'Café Premium', 'Alimentation', 19.99, 45),
('2023-01-08', 'Thé Vert', 'Alimentation', 14.99, 38),
('2023-01-09', 'Biscuits Bio', 'Alimentation', 9.99, 29); 