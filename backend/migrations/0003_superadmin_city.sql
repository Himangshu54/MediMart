ALTER TABLE SUPER_ADMIN
  ADD COLUMN city_id INT NULL AFTER pincode,
  ADD KEY city_id (city_id),
  ADD CONSTRAINT super_admin_ibfk_1 FOREIGN KEY (city_id) REFERENCES CITY (city_id);
