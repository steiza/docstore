CREATE TABLE docs (
	id INTEGER NOT NULL,
	doc_title VARCHAR,
	doc_description VARCHAR,
	source_org VARCHAR,
	tracking_number VARCHAR,
	date_requested DATE,
	date_received DATE,
	uploader_name VARCHAR,
	uploader_email VARCHAR,
	filename VARCHAR,
	date_uploaded DATE,
	PRIMARY KEY (id)
);
