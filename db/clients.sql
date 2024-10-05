CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    id_status INT NOT NULL,
    FOREIGN KEY (id_status) REFERENCES status(id)
);

CREATE INDEX idx_clients_status ON clients(id_status);
