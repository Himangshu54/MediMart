INSERT INTO city (city_name, state) VALUES
('Jorhat', 'Assam'),
('Guwahati', 'Assam'),
('Ferozepur', 'Punjab'),
('Jaipur', 'Rajasthan'),
('Chennai', 'Tamil Nadu');

SELECT * FROM city;
SELECT * FROM super_admin;

ALTER TABLE SUPER_ADMIN
  ADD COLUMN city_id INT NULL AFTER pincode,
  ADD KEY city_id (city_id),
  ADD CONSTRAINT super_admin_ibfk_1 FOREIGN KEY (city_id) REFERENCES CITY (city_id);
