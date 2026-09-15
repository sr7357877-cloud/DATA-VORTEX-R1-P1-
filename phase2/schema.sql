-- Phase 2 Schema Design
CREATE OR REPLACE TABLE users AS SELECT * FROM read_csv_auto('data/cleaned/Social_Engine_Users_Cleaned.csv', header=true);
CREATE OR REPLACE TABLE posts AS SELECT * FROM read_csv_auto('data/cleaned/Social_Engine_Posts_Cleaned.csv', header=true);
